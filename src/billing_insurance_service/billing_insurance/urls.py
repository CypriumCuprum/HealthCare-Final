from django.urls import path
from . import views

urlpatterns = [
    # Patient facing endpoints
    path('invoices/', views.InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    path('patients/<int:patient_id>/invoices/', views.PatientInvoiceListView.as_view(), name='patient-invoice-list'),
    path('invoices/<int:pk>/pay/', views.InvoicePaymentView.as_view(), name='invoice-payment'),
    
    # Insurance policy management
    path('patients/<int:patient_id>/insurance-policies/', views.InsurancePolicyListCreateView.as_view(), name='patient-insurance-list'),
    path('insurance-policies/', views.InsurancePolicyListCreateView.as_view(), name='insurance-policy-list'),
    path('insurance-policies/<int:pk>/', views.InsurancePolicyDetailView.as_view(), name='insurance-policy-detail'),
    
    # Insurance claims
    path('insurance-claims/', views.InsuranceClaimListCreateView.as_view(), name='insurance-claim-list'),
    path('insurance-claims/<int:pk>/', views.InsuranceClaimDetailView.as_view(), name='insurance-claim-detail'),
    
    # Internal APIs for integration with other services
    path('billing/internal/create-invoice-for-appointment/', views.CreateInvoiceForAppointmentView.as_view(), name='create-invoice-appointment'),
    path('billing/internal/create-invoice-for-medication/', views.CreateInvoiceForMedicationView.as_view(), name='create-invoice-medication'),
    path('billing/internal/create-invoice-for-labtest/', views.CreateInvoiceForLabTestView.as_view(), name='create-invoice-labtest'),
] 