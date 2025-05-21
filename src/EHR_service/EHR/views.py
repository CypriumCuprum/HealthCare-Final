from django.shortcuts import render
from rest_framework import permissions, status, viewsets
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
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter medical records based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        user_id = self.request.user.id
        user_role = self.request.user.role.name

        if user_role == 'PATIENT':
            if int(patient_id) != user_id:
                return MedicalRecord.objects.none()
        elif user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
            return MedicalRecord.objects.none()

        return MedicalRecord.objects.filter(patient_id=patient_id)

    def perform_create(self, serializer):
        """Create medical record with patient ID from URL."""
        serializer.save(patient_id=self.kwargs.get('patient_id'))


class EncounterViewSet(viewsets.ModelViewSet):
    """ViewSet for managing encounters."""
    serializer_class = EncounterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter encounters based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        user_id = self.request.user.id
        user_role = self.request.user.role.name

        if user_role == 'PATIENT':
            if int(patient_id) != user_id:
                return Encounter.objects.none()
        elif user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
            return Encounter.objects.none()

        return Encounter.objects.filter(medical_record__patient_id=patient_id)

    def perform_create(self, serializer):
        """Create encounter with medical record from patient ID."""
        medical_record = MedicalRecord.objects.get(patient_id=self.kwargs.get('patient_id'))
        serializer.save(medical_record=medical_record)


class DiagnosisViewSet(viewsets.ModelViewSet):
    """ViewSet for managing diagnoses."""
    serializer_class = DiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter diagnoses based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        user_id = self.request.user.id
        user_role = self.request.user.role.name

        if user_role == 'PATIENT':
            if int(patient_id) != user_id:
                return Diagnosis.objects.none()
        elif user_role not in ['DOCTOR', 'ADMIN']:
            return Diagnosis.objects.none()

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
    serializer_class = TreatmentPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter treatment plans based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        user_id = self.request.user.id
        user_role = self.request.user.role.name

        if user_role == 'PATIENT':
            if int(patient_id) != user_id:
                return TreatmentPlan.objects.none()
        elif user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
            return TreatmentPlan.objects.none()

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
    serializer_class = VitalSignSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter vital signs based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        user_id = self.request.user.id
        user_role = self.request.user.role.name

        if user_role == 'PATIENT':
            if int(patient_id) != user_id:
                return VitalSign.objects.none()
        elif user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
            return VitalSign.objects.none()

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter lab result references based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        user_id = self.request.user.id
        user_role = self.request.user.role.name

        if user_role == 'PATIENT':
            if int(patient_id) != user_id:
                return LabResultReference.objects.none()
        elif user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
            return LabResultReference.objects.none()

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter prescription references based on user role and ID."""
        patient_id = self.kwargs.get('patient_id')
        encounter_id = self.kwargs.get('encounter_id')
        user_id = self.request.user.id
        user_role = self.request.user.role.name

        if user_role == 'PATIENT':
            if int(patient_id) != user_id:
                return PrescriptionReference.objects.none()
        elif user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
            return PrescriptionReference.objects.none()

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
