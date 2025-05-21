import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that gets user details from User Service.
    """
    def authenticate(self, request):
        # Authenticate using JWT
        jwt_auth = super().authenticate(request)
        if jwt_auth is None:
            return None

        # Get user ID and token from JWT
        user, token = jwt_auth

        # Return only the validated token since we don't have the actual user
        return (None, token)


def get_user_details(user_id, token=None):
    """
    Get user details from User Service.
    """
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
        return response.status_code == 200 or response.status_code == 201
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
        return response.status_code == 200 or response.status_code == 201
    except requests.RequestException:
        return False 