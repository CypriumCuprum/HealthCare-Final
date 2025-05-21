from django.contrib import admin

from .models import (
    Diagnosis,
    Encounter,
    LabResultReference,
    MedicalRecord,
    PrescriptionReference,
    TreatmentPlan,
    VitalSign,
)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """Admin configuration for MedicalRecord model."""
    list_display = ('id', 'patient_id', 'patient_name', 'blood_type', 'created_at')
    search_fields = ('patient_id', 'patient_name')
    list_filter = ('blood_type', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    """Admin configuration for Encounter model."""
    list_display = ('id', 'medical_record', 'doctor_id', 'doctor_name', 'encounter_date')
    search_fields = ('doctor_id', 'doctor_name', 'appointment_id')
    list_filter = ('encounter_date', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    """Admin configuration for Diagnosis model."""
    list_display = ('id', 'encounter', 'icd_code', 'description', 'is_primary')
    search_fields = ('icd_code', 'description')
    list_filter = ('is_primary', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TreatmentPlan)
class TreatmentPlanAdmin(admin.ModelAdmin):
    """Admin configuration for TreatmentPlan model."""
    list_display = ('id', 'encounter', 'created_at')
    search_fields = ('description', 'follow_up_instructions')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    """Admin configuration for VitalSign model."""
    list_display = ('id', 'encounter', 'nurse_id', 'timestamp', 'heart_rate', 'blood_pressure')
    search_fields = ('nurse_id',)
    list_filter = ('timestamp', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LabResultReference)
class LabResultReferenceAdmin(admin.ModelAdmin):
    """Admin configuration for LabResultReference model."""
    list_display = ('id', 'encounter', 'lab_order_item_id', 'test_name')
    search_fields = ('lab_order_item_id', 'test_name')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PrescriptionReference)
class PrescriptionReferenceAdmin(admin.ModelAdmin):
    """Admin configuration for PrescriptionReference model."""
    list_display = ('id', 'encounter', 'prescription_id', 'issue_date')
    search_fields = ('prescription_id',)
    list_filter = ('issue_date', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
