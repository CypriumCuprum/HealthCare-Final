from django.urls import path
from . import views

urlpatterns = [
    # Medication catalog
    path('medications/catalog/', views.MedicationListCreateView.as_view(), name='medication-list-create'),
    path('medications/catalog/<int:pk>/', views.MedicationDetailView.as_view(), name='medication-detail'),
    
    # Prescriptions - Doctor endpoints
    path('prescriptions/', views.PrescriptionListCreateView.as_view(), name='prescription-list-create'),
    path('prescriptions/<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription-detail'),
    
    # Patient endpoints
    path('patients/<int:patient_id>/prescriptions/', views.PatientPrescriptionListView.as_view(), name='patient-prescription-list'),
    
    # Pharmacist endpoints
    path('pharmacy/prescriptions/pending/', views.PendingPrescriptionListView.as_view(), name='pending-prescription-list'),
    path('pharmacy/prescriptions/<int:pk>/verify/', views.VerifyPrescriptionView.as_view(), name='verify-prescription'),
    path('pharmacy/prescriptions/<int:pk>/dispense/', views.DispensePrescriptionView.as_view(), name='dispense-prescription'),
    
    # Pharmacy stock management
    path('pharmacy/stock/', views.PharmacyStockListView.as_view(), name='pharmacy-stock-list'),
    path('pharmacy/stock/<int:pk>/', views.PharmacyStockUpdateView.as_view(), name='pharmacy-stock-update'),
] 