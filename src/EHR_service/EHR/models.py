from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class MedicalRecord(models.Model):
    """Model for storing medical records."""
    patient_id = models.IntegerField(
        _('Patient ID'),
        help_text=_('ID from User Service')
    )
    patient_name = models.CharField(
        _('Patient Name'),
        max_length=255,
        help_text=_('Denormalized for convenience')
    )
    blood_type = models.CharField(
        _('Blood Type'),
        max_length=10,
        blank=True,
        null=True
    )
    allergies = models.JSONField(
        _('Allergies'),
        default=list,
        help_text=_('List of allergies')
    )
    chronic_conditions = models.JSONField(
        _('Chronic Conditions'),
        default=list,
        help_text=_('List of chronic conditions')
    )
    medical_history_summary = models.TextField(
        _('Medical History Summary'),
        blank=True
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Medical Record')
        verbose_name_plural = _('Medical Records')
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Medical Record for {self.patient_name}"


class Encounter(models.Model):
    """Model for storing medical encounters."""
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='encounters',
        verbose_name=_('Medical Record')
    )
    encounter_id = models.UUIDField(
        _('Encounter ID'),
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unique ID for encounter')
    )
    doctor_id = models.IntegerField(
        _('Doctor ID'),
        help_text=_('ID from User Service')
    )
    doctor_name = models.CharField(
        _('Doctor Name'),
        max_length=255,
        help_text=_('Denormalized for convenience')
    )
    appointment_id = models.CharField(
        _('Appointment ID'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('ID from Appointment Service')
    )
    encounter_date = models.DateTimeField(
        _('Encounter Date')
    )
    chief_complaint = models.TextField(
        _('Chief Complaint')
    )
    history_of_present_illness = models.TextField(
        _('History of Present Illness'),
        blank=True
    )
    physical_examination_findings = models.TextField(
        _('Physical Examination Findings'),
        blank=True
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Encounter')
        verbose_name_plural = _('Encounters')
        indexes = [
            models.Index(fields=['medical_record']),
            models.Index(fields=['doctor_id']),
            models.Index(fields=['encounter_date']),
        ]

    def __str__(self):
        return f"Encounter {self.encounter_id} for {self.medical_record.patient_name}"


class Diagnosis(models.Model):
    """Model for storing diagnoses."""
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name='diagnoses',
        verbose_name=_('Encounter')
    )
    diagnosis_id = models.UUIDField(
        _('Diagnosis ID'),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    icd_code = models.CharField(
        _('ICD Code'),
        max_length=20
    )
    description = models.CharField(
        _('Description'),
        max_length=255
    )
    is_primary = models.BooleanField(
        _('Is Primary'),
        default=False
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Diagnosis')
        verbose_name_plural = _('Diagnoses')
        indexes = [
            models.Index(fields=['encounter']),
            models.Index(fields=['icd_code']),
        ]

    def __str__(self):
        return f"{self.description} ({self.icd_code})"


class TreatmentPlan(models.Model):
    """Model for storing treatment plans."""
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name='treatment_plans',
        verbose_name=_('Encounter')
    )
    treatment_plan_id = models.UUIDField(
        _('Treatment Plan ID'),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    description = models.TextField(
        _('Description')
    )
    follow_up_instructions = models.TextField(
        _('Follow-up Instructions'),
        blank=True
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Treatment Plan')
        verbose_name_plural = _('Treatment Plans')
        indexes = [
            models.Index(fields=['encounter']),
        ]

    def __str__(self):
        return f"Treatment Plan for {self.encounter}"


class VitalSign(models.Model):
    """Model for storing vital signs."""
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name='vital_signs',
        verbose_name=_('Encounter')
    )
    vital_id = models.UUIDField(
        _('Vital ID'),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    nurse_id = models.IntegerField(
        _('Nurse ID'),
        help_text=_('ID from User Service')
    )
    timestamp = models.DateTimeField(
        _('Timestamp')
    )
    heart_rate = models.IntegerField(
        _('Heart Rate'),
        blank=True,
        null=True
    )
    blood_pressure = models.CharField(
        _('Blood Pressure'),
        max_length=20,
        blank=True,
        null=True
    )
    temperature_celsius = models.DecimalField(
        _('Temperature (Celsius)'),
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Vital Sign')
        verbose_name_plural = _('Vital Signs')
        indexes = [
            models.Index(fields=['encounter']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Vital Signs for {self.encounter} at {self.timestamp}"


class LabResultReference(models.Model):
    """Model for storing references to lab results."""
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name='lab_result_references',
        verbose_name=_('Encounter')
    )
    lab_order_item_id = models.CharField(
        _('Lab Order Item ID'),
        max_length=100,
        help_text=_('ID from Laboratory Service')
    )
    test_name = models.CharField(
        _('Test Name'),
        max_length=255
    )
    result_summary_url = models.URLField(
        _('Result Summary URL'),
        max_length=500
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Lab Result Reference')
        verbose_name_plural = _('Lab Result References')
        indexes = [
            models.Index(fields=['encounter']),
            models.Index(fields=['lab_order_item_id']),
        ]

    def __str__(self):
        return f"Lab Result Reference for {self.test_name}"


class PrescriptionReference(models.Model):
    """Model for storing references to prescriptions."""
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name='prescription_references',
        verbose_name=_('Encounter')
    )
    prescription_id = models.CharField(
        _('Prescription ID'),
        max_length=100,
        help_text=_('ID from Prescription Service')
    )
    issue_date = models.DateTimeField(
        _('Issue Date')
    )
    prescription_details_url = models.URLField(
        _('Prescription Details URL'),
        max_length=500
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Prescription Reference')
        verbose_name_plural = _('Prescription References')
        indexes = [
            models.Index(fields=['encounter']),
            models.Index(fields=['prescription_id']),
        ]

    def __str__(self):
        return f"Prescription Reference {self.prescription_id}"
