import requests
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework import authentication, exceptions
from rest_framework.authentication import BaseAuthentication

from .authentication import SimpleTokenAuthentication


class CustomTokenAuthentication(BaseAuthentication):
    """
    Custom token authentication for Billing & Insurance Service.
    """
    def authenticate(self, request):
        # Delegate to SimpleTokenAuthentication
        authenticator = SimpleTokenAuthentication()
        return authenticator.authenticate(request)

    def authenticate_header(self, request):
        return 'Bearer'


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


def notify_notification_service(notification_type, recipient_id, data, token=None):
    """
    Send notification using the Notification Service.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    notification_data = {
        'notification_type': notification_type,
        'recipient_id': recipient_id,
        'data': data
    }

    try:
        response = requests.post(
            f"{settings.NOTIFICATION_SERVICE_URL}/notifications/send/",
            json=notification_data,
            headers=headers
        )
        return response.status_code in [200, 201, 202]
    except requests.RequestException:
        return False


def generate_invoice_number():
    """
    Generate a unique invoice number.
    """
    from .models import Invoice
    
    # Format: INV-YYYYMMDD-COUNT
    today = datetime.now().strftime('%Y%m%d')
    
    # Count invoices for today to determine the sequence number
    count = Invoice.objects.filter(
        invoice_number__startswith=f'INV-{today}'
    ).count()
    
    # Return formatted invoice number
    return f'INV-{today}-{count+1:04d}'


def calculate_due_date(issue_date=None, days=30):
    """
    Calculate due date from issue date.
    """
    if not issue_date:
        issue_date = datetime.now().date()
    return issue_date + timedelta(days=days) 