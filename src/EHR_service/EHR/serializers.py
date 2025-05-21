from rest_framework import serializers

from .models import (
    Diagnosis,
    Encounter,
    LabResultReference,
    MedicalRecord,
    PrescriptionReference,
    TreatmentPlan,
    VitalSign,
)


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer for the MedicalRecord model."""
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient_id', 'patient_name', 'blood_type',
            'allergies', 'chronic_conditions', 'medical_history_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EncounterSerializer(serializers.ModelSerializer):
    """Serializer for the Encounter model."""
    class Meta:
        model = Encounter
        fields = [
            'id', 'medical_record', 'doctor_id', 'doctor_name',
            'appointment_id', 'encounter_date', 'chief_complaint',
            'history_of_present_illness', 'physical_examination_findings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DiagnosisSerializer(serializers.ModelSerializer):
    """Serializer for the Diagnosis model."""
    class Meta:
        model = Diagnosis
        fields = [
            'id', 'encounter', 'icd_code', 'description',
            'is_primary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TreatmentPlanSerializer(serializers.ModelSerializer):
    """Serializer for the TreatmentPlan model."""
    class Meta:
        model = TreatmentPlan
        fields = [
            'id', 'encounter', 'description',
            'follow_up_instructions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VitalSignSerializer(serializers.ModelSerializer):
    """Serializer for the VitalSign model."""
    class Meta:
        model = VitalSign
        fields = [
            'id', 'encounter', 'nurse_id', 'timestamp',
            'heart_rate', 'blood_pressure', 'temperature_celsius',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LabResultReferenceSerializer(serializers.ModelSerializer):
    """Serializer for the LabResultReference model."""
    class Meta:
        model = LabResultReference
        fields = [
            'id', 'encounter', 'lab_order_item_id',
            'test_name', 'result_summary_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PrescriptionReferenceSerializer(serializers.ModelSerializer):
    """Serializer for the PrescriptionReference model."""
    class Meta:
        model = PrescriptionReference
        fields = [
            'id', 'encounter', 'prescription_id',
            'issue_date', 'prescription_details_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 