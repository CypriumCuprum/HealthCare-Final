from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DiagnosisViewSet,
    EncounterViewSet,
    LabResultReferenceViewSet,
    MedicalRecordViewSet,
    PrescriptionReferenceViewSet,
    TreatmentPlanViewSet,
    VitalSignViewSet,
)

router = DefaultRouter()
router.register(r'patients/(?P<patient_id>\d+)/records', MedicalRecordViewSet, basename='medical-record')
router.register(r'patients/(?P<patient_id>\d+)/encounters', EncounterViewSet, basename='encounter')
router.register(r'patients/(?P<patient_id>\d+)/encounters/(?P<encounter_id>[^/.]+)/diagnoses', DiagnosisViewSet, basename='diagnosis')
router.register(r'patients/(?P<patient_id>\d+)/encounters/(?P<encounter_id>[^/.]+)/treatment-plans', TreatmentPlanViewSet, basename='treatment-plan')
router.register(r'patients/(?P<patient_id>\d+)/encounters/(?P<encounter_id>[^/.]+)/vital-signs', VitalSignViewSet, basename='vital-sign')
router.register(r'patients/(?P<patient_id>\d+)/encounters/(?P<encounter_id>[^/.]+)/lab-results', LabResultReferenceViewSet, basename='lab-result')
router.register(r'patients/(?P<patient_id>\d+)/encounters/(?P<encounter_id>[^/.]+)/prescriptions', PrescriptionReferenceViewSet, basename='prescription')

urlpatterns = [
    path('', include(router.urls)),
] 