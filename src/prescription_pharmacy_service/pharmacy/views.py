from django.shortcuts import render, get_object_or_404
from django.db import transaction
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    Medication, Prescription, PrescriptionItem, 
    PharmacyStock, BatchExpiry, DispenseLog, DispenseItem
)
from .serializers import (
    MedicationSerializer, PrescriptionSerializer, 
    PharmacyStockSerializer, PrescriptionDispenseSerializer,
    MedicationStockUpdateSerializer
)
from .utils import notify_ehr_service, notify_billing_service


class MedicationListCreateView(generics.ListCreateAPIView):
    """List and create medications"""
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    

class MedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a medication"""
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer


class PrescriptionListCreateView(generics.ListCreateAPIView):
    """List and create prescriptions"""
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    
    def perform_create(self, serializer):
        prescription = serializer.save()
        # Notify EHR service about the new prescription
        notify_ehr_service(
            prescription_id=prescription.id,
            patient_id=prescription.patient_id,
            issue_date=prescription.date_prescribed.isoformat(),
            token=self.request.auth
        )
        return prescription


class PrescriptionDetailView(generics.RetrieveAPIView):
    """Retrieve a prescription"""
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer


class PatientPrescriptionListView(generics.ListAPIView):
    """List prescriptions for a specific patient"""
    serializer_class = PrescriptionSerializer
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return Prescription.objects.filter(patient_id=patient_id)


class PendingPrescriptionListView(generics.ListAPIView):
    """List pending prescriptions for pharmacist verification"""
    serializer_class = PrescriptionSerializer
    
    def get_queryset(self):
        return Prescription.objects.filter(
            status__in=['PENDING_VERIFICATION', 'VERIFIED']
        )


class VerifyPrescriptionView(views.APIView):
    """Verify a prescription by pharmacist"""
    def post(self, request, pk):
        prescription = get_object_or_404(Prescription, pk=pk)
        
        if prescription.status != 'PENDING_VERIFICATION':
            return Response(
                {"detail": "Only prescriptions with PENDING_VERIFICATION status can be verified."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prescription.status = 'VERIFIED'
        prescription.save()
        
        return Response(
            {"detail": "Prescription verified successfully."},
            status=status.HTTP_200_OK
        )


class DispensePrescriptionView(views.APIView):
    """Dispense medications for a prescription"""
    @transaction.atomic
    def post(self, request, pk):
        prescription = get_object_or_404(Prescription, pk=pk)
        
        if prescription.status not in ['VERIFIED', 'DISPENSED_PARTIAL']:
            return Response(
                {"detail": "Only VERIFIED or DISPENSED_PARTIAL prescriptions can be dispensed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PrescriptionDispenseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create dispense log
        dispense_log = DispenseLog.objects.create(
            prescription=prescription,
            pharmacist_id=serializer.validated_data['pharmacist_id'],
            pharmacist_name=serializer.validated_data['pharmacist_name'],
            notes=serializer.validated_data.get('notes', '')
        )
        
        items_data = serializer.validated_data['items_dispensed']
        billing_items = []
        all_items_dispensed = True
        
        for item_data in items_data:
            prescription_item_id = item_data.get('prescription_item_id')
            quantity_dispensed = item_data.get('quantity_dispensed')
            batch_number = item_data.get('batch_number')
            
            prescription_item = get_object_or_404(PrescriptionItem, pk=prescription_item_id)
            
            # Check if we're dispensing more than prescribed
            if prescription_item.quantity_dispensed + quantity_dispensed > prescription_item.quantity_prescribed:
                return Response(
                    {"detail": f"Cannot dispense more than prescribed for item {prescription_item_id}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if we have enough stock
            try:
                stock = PharmacyStock.objects.get(medication=prescription_item.medication)
                if stock.quantity_on_hand < quantity_dispensed:
                    return Response(
                        {"detail": f"Insufficient stock for medication {prescription_item.medication.name}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Reduce stock
                stock.quantity_on_hand -= quantity_dispensed
                stock.save()
                
            except PharmacyStock.DoesNotExist:
                return Response(
                    {"detail": f"No stock record for medication {prescription_item.medication.name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create dispense item
            dispense_item = DispenseItem.objects.create(
                dispense_log=dispense_log,
                prescription_item=prescription_item,
                medication=prescription_item.medication,
                quantity_dispensed=quantity_dispensed,
                batch_number=batch_number
            )
            
            # Update prescription item's dispensed quantity
            prescription_item.quantity_dispensed += quantity_dispensed
            prescription_item.save()
            
            # Check if any items are not fully dispensed
            if prescription_item.quantity_dispensed < prescription_item.quantity_prescribed:
                all_items_dispensed = False
            
            # Add to billing items
            billing_items.append({
                "medication_name": prescription_item.medication.name,
                "quantity": quantity_dispensed,
                "unit_price": float(prescription_item.medication.unit_price),
                "total_price": float(prescription_item.medication.unit_price) * quantity_dispensed
            })
        
        # Update prescription status
        if all_items_dispensed:
            prescription.status = 'DISPENSED_FULL'
        else:
            prescription.status = 'DISPENSED_PARTIAL'
        prescription.save()
        
        # Notify billing service
        notify_billing_service(
            dispense_log_id=str(dispense_log.id),
            patient_id=prescription.patient_id,
            items=billing_items,
            token=request.auth
        )
        
        return Response(
            {"detail": "Medications dispensed successfully."},
            status=status.HTTP_200_OK
        )


class PharmacyStockListView(generics.ListAPIView):
    """List all pharmacy stock items"""
    queryset = PharmacyStock.objects.all()
    serializer_class = PharmacyStockSerializer


class PharmacyStockUpdateView(views.APIView):
    """Update pharmacy stock (add inventory)"""
    @transaction.atomic
    def post(self, request, pk):
        stock = get_object_or_404(PharmacyStock, pk=pk)
        serializer = MedicationStockUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        quantity_to_add = serializer.validated_data['quantity_to_add']
        batch_number = serializer.validated_data['batch_number']
        expiry_date = serializer.validated_data['expiry_date']
        
        # Add to overall stock quantity
        stock.quantity_on_hand += quantity_to_add
        stock.last_stocked_date = stock.last_stocked_date
        stock.save()
        
        # Add batch information
        batch = BatchExpiry.objects.create(
            pharmacy_stock=stock,
            batch_number=batch_number,
            quantity=quantity_to_add,
            expiry_date=expiry_date
        )
        
        return Response(
            {"detail": "Stock updated successfully."},
            status=status.HTTP_200_OK
        )
