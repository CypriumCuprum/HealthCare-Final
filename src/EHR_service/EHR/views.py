from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Diagnosis,
    Encounter,
    LabResultReference,
    MedicalRecord,
    PrescriptionReference,
    TreatmentPlan,
    VitalSign,
)
from .serializers import (
    DiagnosisSerializer,
    EncounterSerializer,
    LabResultReferenceSerializer,
    MedicalRecordSerializer,
    PrescriptionReferenceSerializer,
    TreatmentPlanSerializer,
    VitalSignSerializer,
)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for managing medical records."""
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.AllowAny]  # Allow all requests

    def get_queryset(self):
        """Filter medical records based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        return MedicalRecord.objects.filter(patient_id=patient_id)

    def perform_create(self, serializer):
        """Create medical record with patient ID from URL."""
        serializer.save(patient_id=self.kwargs.get('patient_id'))


class EncounterViewSet(viewsets.ModelViewSet):
    """ViewSet for managing encounters."""
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
    permission_classes = [permissions.AllowAny]  # Allow all requests

    def get_queryset(self):
        """Filter encounters based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        return Encounter.objects.filter(medical_record__patient_id=patient_id)

    def perform_create(self, serializer):
        """Create encounter with medical record from patient ID."""
        patient_id = self.kwargs.get('patient_id')
        medical_record = MedicalRecord.objects.filter(patient_id=patient_id).first()
        
        if not medical_record:
            # If no medical record exists, create one
            medical_record = MedicalRecord.objects.create(
                patient_id=patient_id,
                patient_name=f"Patient {patient_id}"  # Default name
            )
        
        serializer.save(medical_record=medical_record)


class DiagnosisViewSet(viewsets.ModelViewSet):
    """ViewSet for managing diagnoses."""
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer
    permission_classes = [permissions.AllowAny]  # Allow all requests

    def get_queryset(self):
        """Filter diagnoses based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        return Diagnosis.objects.filter(
            encounter__medical_record__patient_id=patient_id,
            encounter_id=encounter_id
        )

    def perform_create(self, serializer):
        """Create diagnosis with encounter from URL."""
        encounter = Encounter.objects.get(
            medical_record__patient_id=self.kwargs.get('patient_id'),
            id=self.kwargs.get('encounter_id')
        )
        serializer.save(encounter=encounter)


class TreatmentPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for managing treatment plans."""
    queryset = TreatmentPlan.objects.all()
    serializer_class = TreatmentPlanSerializer
    permission_classes = [permissions.AllowAny]  # Allow all requests

    def get_queryset(self):
        """Filter treatment plans based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        return TreatmentPlan.objects.filter(
            encounter__medical_record__patient_id=patient_id,
            encounter_id=encounter_id
        )

    def perform_create(self, serializer):
        """Create treatment plan with encounter from URL."""
        encounter = Encounter.objects.get(
            medical_record__patient_id=self.kwargs.get('patient_id'),
            id=self.kwargs.get('encounter_id')
        )
        serializer.save(encounter=encounter)


class VitalSignViewSet(viewsets.ModelViewSet):
    """ViewSet for managing vital signs."""
    queryset = VitalSign.objects.all()
    serializer_class = VitalSignSerializer
    permission_classes = [permissions.AllowAny]  # Allow all requests

    def get_queryset(self):
        """Filter vital signs based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        return VitalSign.objects.filter(
            encounter__medical_record__patient_id=patient_id,
            encounter_id=encounter_id
        )

    def perform_create(self, serializer):
        """Create vital sign with encounter from URL."""
        encounter = Encounter.objects.get(
            medical_record__patient_id=self.kwargs.get('patient_id'),
            id=self.kwargs.get('encounter_id')
        )
        serializer.save(encounter=encounter)


class LabResultReferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lab result references."""
    serializer_class = LabResultReferenceSerializer
    permission_classes = [permissions.AllowAny]  # Allow all requests

    def get_queryset(self):
        """Filter lab result references based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        return LabResultReference.objects.filter(
            encounter__medical_record__patient_id=patient_id,
            encounter_id=encounter_id
        )

    def perform_create(self, serializer):
        """Create lab result reference with encounter from URL."""
        encounter = Encounter.objects.get(
            medical_record__patient_id=self.kwargs.get('patient_id'),
            id=self.kwargs.get('encounter_id')
        )
        serializer.save(encounter=encounter)


class PrescriptionReferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing prescription references."""
    serializer_class = PrescriptionReferenceSerializer
    permission_classes = [permissions.AllowAny]  # Allow all requests

    def get_queryset(self):
        """Filter prescription references based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        return PrescriptionReference.objects.filter(
            encounter__medical_record__patient_id=patient_id,
            encounter_id=encounter_id
        )

    def perform_create(self, serializer):
        """Create prescription reference with encounter from URL."""
        encounter = Encounter.objects.get(
            medical_record__patient_id=self.kwargs.get('patient_id'),
            id=self.kwargs.get('encounter_id')
        )
        serializer.save(encounter=encounter)
