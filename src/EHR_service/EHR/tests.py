from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Diagnosis,
    Encounter,
    LabResultReference,
    MedicalRecord,
    PrescriptionReference,
    TreatmentPlan,
    VitalSign,
)


class MedicalRecordTests(APITestCase):
    """Test cases for MedicalRecord endpoints."""

    def setUp(self):
        """Set up test data."""
        self.medical_record = MedicalRecord.objects.create(
            patient_id=1,
            patient_name='Test Patient',
            blood_type='O+',
            allergies=['Penicillin'],
            chronic_conditions=['Hypertension'],
            medical_history_summary='Test history'
        )
        self.url = reverse('medical-record-detail', kwargs={
            'patient_id': 1,
            'pk': self.medical_record.id
        })

    def test_get_medical_record(self):
        """Test retrieving a medical record."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['patient_name'], 'Test Patient')


class EncounterTests(APITestCase):
    """Test cases for Encounter endpoints."""

    def setUp(self):
        """Set up test data."""
        self.medical_record = MedicalRecord.objects.create(
            patient_id=1,
            patient_name='Test Patient'
        )
        self.encounter = Encounter.objects.create(
            medical_record=self.medical_record,
            doctor_id=1,
            doctor_name='Dr. Test',
            encounter_date='2024-02-20T10:00:00Z'
        )
        self.url = reverse('encounter-detail', kwargs={
            'patient_id': 1,
            'pk': self.encounter.id
        })

    def test_get_encounter(self):
        """Test retrieving an encounter."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['doctor_name'], 'Dr. Test')


class DiagnosisTests(APITestCase):
    """Test cases for Diagnosis endpoints."""

    def setUp(self):
        """Set up test data."""
        self.medical_record = MedicalRecord.objects.create(
            patient_id=1,
            patient_name='Test Patient'
        )
        self.encounter = Encounter.objects.create(
            medical_record=self.medical_record,
            doctor_id=1,
            doctor_name='Dr. Test'
        )
        self.diagnosis = Diagnosis.objects.create(
            encounter=self.encounter,
            icd_code='R51',
            description='Headache',
            is_primary=True
        )
        self.url = reverse('diagnosis-detail', kwargs={
            'patient_id': 1,
            'encounter_id': self.encounter.id,
            'pk': self.diagnosis.id
        })

    def test_get_diagnosis(self):
        """Test retrieving a diagnosis."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['icd_code'], 'R51')


class TreatmentPlanTests(APITestCase):
    """Test cases for TreatmentPlan endpoints."""

    def setUp(self):
        """Set up test data."""
        self.medical_record = MedicalRecord.objects.create(
            patient_id=1,
            patient_name='Test Patient'
        )
        self.encounter = Encounter.objects.create(
            medical_record=self.medical_record,
            doctor_id=1,
            doctor_name='Dr. Test'
        )
        self.treatment_plan = TreatmentPlan.objects.create(
            encounter=self.encounter,
            description='Rest and medication',
            follow_up_instructions='Return in 1 week'
        )
        self.url = reverse('treatment-plan-detail', kwargs={
            'patient_id': 1,
            'encounter_id': self.encounter.id,
            'pk': self.treatment_plan.id
        })

    def test_get_treatment_plan(self):
        """Test retrieving a treatment plan."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Rest and medication')


class VitalSignTests(APITestCase):
    """Test cases for VitalSign endpoints."""

    def setUp(self):
        """Set up test data."""
        self.medical_record = MedicalRecord.objects.create(
            patient_id=1,
            patient_name='Test Patient'
        )
        self.encounter = Encounter.objects.create(
            medical_record=self.medical_record,
            doctor_id=1,
            doctor_name='Dr. Test'
        )
        self.vital_sign = VitalSign.objects.create(
            encounter=self.encounter,
            nurse_id=1,
            heart_rate=80,
            blood_pressure='120/80',
            temperature_celsius=37.0
        )
        self.url = reverse('vital-sign-detail', kwargs={
            'patient_id': 1,
            'encounter_id': self.encounter.id,
            'pk': self.vital_sign.id
        })

    def test_get_vital_sign(self):
        """Test retrieving vital signs."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['heart_rate'], 80)


class LabResultReferenceTests(APITestCase):
    """Test cases for LabResultReference endpoints."""

    def setUp(self):
        """Set up test data."""
        self.medical_record = MedicalRecord.objects.create(
            patient_id=1,
            patient_name='Test Patient'
        )
        self.encounter = Encounter.objects.create(
            medical_record=self.medical_record,
            doctor_id=1,
            doctor_name='Dr. Test'
        )
        self.lab_result = LabResultReference.objects.create(
            encounter=self.encounter,
            lab_order_item_id='LAB001',
            test_name='Blood Test',
            result_summary_url='http://example.com/results'
        )
        self.url = reverse('lab-result-detail', kwargs={
            'patient_id': 1,
            'encounter_id': self.encounter.id,
            'pk': self.lab_result.id
        })

    def test_get_lab_result(self):
        """Test retrieving a lab result reference."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['test_name'], 'Blood Test')


class PrescriptionReferenceTests(APITestCase):
    """Test cases for PrescriptionReference endpoints."""

    def setUp(self):
        """Set up test data."""
        self.medical_record = MedicalRecord.objects.create(
            patient_id=1,
            patient_name='Test Patient'
        )
        self.encounter = Encounter.objects.create(
            medical_record=self.medical_record,
            doctor_id=1,
            doctor_name='Dr. Test'
        )
        self.prescription = PrescriptionReference.objects.create(
            encounter=self.encounter,
            prescription_id='PRES001',
            issue_date='2024-02-20',
            prescription_details_url='http://example.com/prescription'
        )
        self.url = reverse('prescription-detail', kwargs={
            'patient_id': 1,
            'encounter_id': self.encounter.id,
            'pk': self.prescription.id
        })

    def test_get_prescription(self):
        """Test retrieving a prescription reference."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['prescription_id'], 'PRES001')
