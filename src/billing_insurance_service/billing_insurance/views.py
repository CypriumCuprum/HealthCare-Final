from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status, permissions, views
from rest_framework.response import Response

from .models import Invoice, InvoiceItem, Payment, InsurancePolicy, InsuranceClaim
from .serializers import (
    InvoiceSerializer, InvoiceItemSerializer, PaymentSerializer,
    InsurancePolicySerializer, InsuranceClaimSerializer,
    InvoicePaymentSerializer, 
    CreateInvoiceForAppointmentSerializer,
    CreateInvoiceForMedicationSerializer,
    CreateInvoiceForLabTestSerializer
)
from .utils import notify_notification_service, generate_invoice_number, calculate_due_date, CustomTokenAuthentication


class InvoiceListCreateView(generics.ListCreateAPIView):
    """List and create invoices"""
    queryset = Invoice.objects.all().order_by('-created_at')
    serializer_class = InvoiceSerializer
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by patient_id if provided
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
            
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset


class InvoiceDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update an invoice"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class PatientInvoiceListView(generics.ListAPIView):
    """List invoices for a specific patient"""
    serializer_class = InvoiceSerializer
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return Invoice.objects.filter(patient_id=patient_id).order_by('-created_at')


class InvoicePaymentView(views.APIView):
    """Process a payment for an invoice"""
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        
        # Check if invoice is already paid
        if invoice.is_paid:
            return Response(
                {"detail": "Invoice is already fully paid."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = InvoicePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        amount = serializer.validated_data['amount']
        payment_method = serializer.validated_data['payment_method']
        transaction_id = serializer.validated_data.get('transaction_id', '')
        notes = serializer.validated_data.get('notes', '')
        
        # Check if payment amount is valid
        if amount <= 0:
            return Response(
                {"detail": "Payment amount must be greater than zero."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if amount > invoice.amount_due:
            return Response(
                {"detail": f"Payment amount (${amount}) exceeds outstanding balance (${invoice.amount_due})."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Create payment record
        payment = Payment.objects.create(
            invoice=invoice,
            patient_id=invoice.patient_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            status='SUCCESS',
            notes=notes
        )
        
        # Update invoice paid amount
        invoice.amount_paid_by_patient += amount
        
        # Update invoice status
        if invoice.is_paid:
            invoice.status = 'PAID'
        elif invoice.status == 'PENDING_PATIENT' and invoice.amount_paid_by_patient > 0:
            invoice.status = 'PARTIALLY_PAID'
            
        invoice.save()
        
        # Notify patient about successful payment
        notify_notification_service(
            notification_type='PAYMENT_SUCCESSFUL',
            recipient_id=invoice.patient_id,
            data={
                "invoice_number": invoice.invoice_number,
                "amount_paid": str(amount),
                "payment_date": payment.payment_date.strftime("%Y-%m-%d %H:%M"),
                "remaining_balance": str(invoice.amount_due)
            },
            token=request.auth
        )
        
        return Response({
            "detail": "Payment processed successfully.",
            "payment_id": payment.id,
            "amount_paid": amount,
            "remaining_balance": invoice.amount_due,
            "invoice_status": invoice.status
        }, status=status.HTTP_200_OK)


class InsurancePolicyListCreateView(generics.ListCreateAPIView):
    """List and create insurance policies"""
    serializer_class = InsurancePolicySerializer
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filter by patient_id if provided in URL
        patient_id = self.request.query_params.get('patient_id') or self.kwargs.get('patient_id')
        if patient_id:
            return InsurancePolicy.objects.filter(patient_id=patient_id).order_by('-created_at')
        return InsurancePolicy.objects.all().order_by('-created_at')


class InsurancePolicyDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update an insurance policy"""
    queryset = InsurancePolicy.objects.all()
    serializer_class = InsurancePolicySerializer
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class InsuranceClaimListCreateView(generics.ListCreateAPIView):
    """List and create insurance claims"""
    serializer_class = InsuranceClaimSerializer
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filter by invoice_id if provided
        invoice_id = self.request.query_params.get('invoice_id')
        if invoice_id:
            return InsuranceClaim.objects.filter(invoice_id=invoice_id).order_by('-created_at')
        return InsuranceClaim.objects.all().order_by('-created_at')
    
    @transaction.atomic    
    def perform_create(self, serializer):
        claim = serializer.save()
        
        # Update invoice status
        invoice = claim.invoice
        if invoice.status == 'PENDING_PATIENT' or invoice.status == 'PARTIALLY_PAID':
            invoice.status = 'PENDING_INSURANCE'
            invoice.save()
            
        # Notify about claim submission
        notify_notification_service(
            notification_type='INSURANCE_CLAIM_SUBMITTED',
            recipient_id=invoice.patient_id,
            data={
                "invoice_number": invoice.invoice_number,
                "claim_amount": str(claim.claim_amount),
                "submission_date": claim.submission_date.strftime("%Y-%m-%d"),
                "provider_name": claim.insurance_policy.provider_name
            },
            token=self.request.auth
        )


class InsuranceClaimDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update an insurance claim"""
    queryset = InsuranceClaim.objects.all()
    serializer_class = InsuranceClaimSerializer
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def perform_update(self, serializer):
        old_status = self.get_object().status
        claim = serializer.save()
        new_status = claim.status
        
        # If status changed to approved or partially approved
        if old_status != new_status and new_status in ['APPROVED', 'PARTIALLY_APPROVED']:
            # Update invoice with insurance payment amount
            invoice = claim.invoice
            
            # For simplicity, we assume the approved amount will be paid by insurance
            if claim.approved_amount:
                insurance_payment = Payment.objects.create(
                    invoice=invoice,
                    patient_id=invoice.patient_id,
                    amount=claim.approved_amount,
                    payment_method='INSURANCE_PAYOUT',
                    status='SUCCESS',
                    notes=f"Insurance payment for claim #{claim.id}"
                )
                
                invoice.amount_paid_by_insurance = claim.approved_amount
                
                # Update invoice status
                if invoice.is_paid:
                    invoice.status = 'PAID'
                else:
                    invoice.status = 'PARTIALLY_PAID'
                    
                invoice.save()
                
                # Notify patient about claim approval
                notify_notification_service(
                    notification_type='INSURANCE_CLAIM_APPROVED',
                    recipient_id=invoice.patient_id,
                    data={
                        "invoice_number": invoice.invoice_number,
                        "approved_amount": str(claim.approved_amount),
                        "provider_name": claim.insurance_policy.provider_name,
                        "remaining_balance": str(invoice.amount_due)
                    },
                    token=self.request.auth
                )


# Internal API endpoints
class CreateInvoiceForAppointmentView(views.APIView):
    """Internal API to create invoice for an appointment"""
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = CreateInvoiceForAppointmentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # Extract data
        appointment_id = serializer.validated_data['appointment_id']
        patient_id = serializer.validated_data['patient_id']
        doctor_id = serializer.validated_data['doctor_id']
        service_description = serializer.validated_data['service_description']
        amount = serializer.validated_data['amount']
        
        # Create invoice
        invoice = Invoice.objects.create(
            patient_id=patient_id,
            invoice_number=generate_invoice_number(),
            issue_date=timezone.now().date(),
            due_date=calculate_due_date(timezone.now().date()),
            sub_total_amount=amount,
            total_amount=amount,  # No tax/discount for simplicity
            status='PENDING_PATIENT',
            related_appointment_id=appointment_id
        )
        
        # Add invoice item
        invoice_item = InvoiceItem.objects.create(
            invoice=invoice,
            item_type='CONSULTATION',
            description=service_description,
            quantity=1,
            unit_price=amount,
            total_price=amount
        )
        
        # Notify patient about new invoice
        notify_notification_service(
            notification_type='INVOICE_GENERATED',
            recipient_id=patient_id,
            data={
                "invoice_number": invoice.invoice_number,
                "amount": str(amount),
                "due_date": invoice.due_date.strftime("%Y-%m-%d"),
                "service": service_description
            },
            token=request.auth
        )
        
        return Response({
            "detail": "Invoice created successfully for appointment.",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number
        }, status=status.HTTP_201_CREATED)


class CreateInvoiceForMedicationView(views.APIView):
    """Internal API to create invoice for medication dispensed"""
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = CreateInvoiceForMedicationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # Extract data
        dispense_log_id = serializer.validated_data['dispense_log_id']
        patient_id = serializer.validated_data['patient_id']
        items = serializer.validated_data['items']
        
        # Calculate total amount
        total_amount = sum(float(item.get('total_price', 0)) for item in items)
        
        # Create invoice
        invoice = Invoice.objects.create(
            patient_id=patient_id,
            invoice_number=generate_invoice_number(),
            issue_date=timezone.now().date(),
            due_date=calculate_due_date(timezone.now().date()),
            sub_total_amount=total_amount,
            total_amount=total_amount,  # No tax/discount for simplicity
            status='PENDING_PATIENT',
            related_prescription_dispense_id=dispense_log_id
        )
        
        # Add invoice items
        for item in items:
            InvoiceItem.objects.create(
                invoice=invoice,
                item_type='MEDICATION',
                description=item.get('medication_name', 'Medication'),
                quantity=item.get('quantity', 1),
                unit_price=item.get('unit_price', 0),
                total_price=item.get('total_price', 0)
            )
        
        # Notify patient about new invoice
        notify_notification_service(
            notification_type='INVOICE_GENERATED',
            recipient_id=patient_id,
            data={
                "invoice_number": invoice.invoice_number,
                "amount": str(total_amount),
                "due_date": invoice.due_date.strftime("%Y-%m-%d"),
                "service": "Medication"
            },
            token=request.auth
        )
        
        return Response({
            "detail": "Invoice created successfully for medication.",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number
        }, status=status.HTTP_201_CREATED)


class CreateInvoiceForLabTestView(views.APIView):
    """Internal API to create invoice for lab tests"""
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = CreateInvoiceForLabTestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # Extract data
        lab_order_id = serializer.validated_data['lab_order_id']
        patient_id = serializer.validated_data['patient_id']
        items = serializer.validated_data['items']
        
        # Calculate total amount
        total_amount = sum(float(item.get('price', 0)) for item in items)
        
        # Create invoice
        invoice = Invoice.objects.create(
            patient_id=patient_id,
            invoice_number=generate_invoice_number(),
            issue_date=timezone.now().date(),
            due_date=calculate_due_date(timezone.now().date()),
            sub_total_amount=total_amount,
            total_amount=total_amount,  # No tax/discount for simplicity
            status='PENDING_PATIENT',
            related_lab_order_id=lab_order_id
        )
        
        # Add invoice items
        for item in items:
            InvoiceItem.objects.create(
                invoice=invoice,
                item_type='LAB_TEST',
                description=item.get('test_name', 'Laboratory Test'),
                quantity=1,
                unit_price=item.get('price', 0),
                total_price=item.get('price', 0)
            )
        
        # Notify patient about new invoice
        notify_notification_service(
            notification_type='INVOICE_GENERATED',
            recipient_id=patient_id,
            data={
                "invoice_number": invoice.invoice_number,
                "amount": str(total_amount),
                "due_date": invoice.due_date.strftime("%Y-%m-%d"),
                "service": "Laboratory Tests"
            },
            token=request.auth
        )
        
        return Response({
            "detail": "Invoice created successfully for lab tests.",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number
        }, status=status.HTTP_201_CREATED)
