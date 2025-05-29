import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission

from .authentication import SimpleTokenAuthentication


class CustomTokenAuthentication(BaseAuthentication):
    """
    Custom token authentication for Pharmacy Service.
    """
    def authenticate(self, request):
        # Delegate to SimpleTokenAuthentication
        print("authenticate")
        authenticator = SimpleTokenAuthentication()
        return authenticator.authenticate(request)

    def authenticate_header(self, request):
        return 'Bearer'


def get_user_details(user_id, token=None):
    """
    Get user details from User Service.
    """
    print("get_user_details")
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(
            f"{settings.USER_SERVICE_URL}/users/{user_id}/",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException:
        return None


def notify_ehr_service(prescription_id, patient_id, issue_date, token=None):
    """
    Notify EHR Service about a new prescription.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    data = {
        'prescription_id': prescription_id,
        'patient_id': patient_id,
        'issue_date': issue_date,
    }
    
    try:
        response = requests.post(
            f"{settings.EHR_SERVICE_URL}/ehr/internal/patients/{patient_id}/add-prescription-reference/",
            json=data,
            headers=headers
        )
        return response.status_code in [200, 201, 202]
    except requests.RequestException:
        return False


def notify_billing_service(dispense_log_id, patient_id, items, token=None):
    """
    Notify Billing Service about a medication dispense.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    data = {
        'dispense_log_id': dispense_log_id,
        'patient_id': patient_id,
        'items': items
    }
    
    try:
        response = requests.post(
            f"{settings.BILLING_SERVICE_URL}/billing/internal/create-invoice-for-medication/",
            json=data,
            headers=headers
        )
        return response.status_code in [200, 201, 202]
    except requests.RequestException:
        return False


class HasRole(BasePermission):
    """
    Permission class to check if user has specific role.
    Admin can do everything.
    """
    def __init__(self, required_role):
        self.required_role = required_role
    
    def has_permission(self, request, view):
        # ADMIN có quyền làm mọi thứ
        if hasattr(request.user, 'role'):
            if isinstance(request.user.role, dict) and request.user.role.get('name') == 'ADMIN':
                return True
            elif request.user.role == 'ADMIN':
                return True
            
        # Kiểm tra role yêu cầu
        if hasattr(request.user, 'role'):
            if isinstance(request.user.role, dict):
                return request.user.role.get('name') == self.required_role
            return request.user.role == self.required_role
        return False 