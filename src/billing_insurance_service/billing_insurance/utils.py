import requests
from django.conf import settings
from datetime import datetime, timedelta
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
    return {
        'id': user_id,
        'first_name': 'Test',
        'last_name': 'User',
        'email': f'user{user_id}@example.com',
        'role': 'PATIENT'
    }


def notify_notification_service(notification_type, recipient_id, data, token=None):
    """
    Send notification via Notification Service.
    """
    print(f"[NOTIFICATION SKIPPED] Type: {notification_type}, Recipient: {recipient_id}")
    print(f"Notification data: {data}")
    
    return True


def generate_invoice_number():
    """
    Generate a unique invoice number.
    Format: INV-YYYYMMDD-XXXX where XXXX is a sequential number for the day
    """
    from .models import Invoice
    
    today = datetime.now().strftime("%Y%m%d")
    
    # Get latest invoice number for today
    latest_invoice = Invoice.objects.filter(
        invoice_number__startswith=f"INV-{today}"
    ).order_by('-invoice_number').first()
    
    if latest_invoice:
        # Extract the sequence number and increment it
        try:
            seq_num = int(latest_invoice.invoice_number.split('-')[-1])
            next_seq = seq_num + 1
        except (ValueError, IndexError):
            next_seq = 1
    else:
        next_seq = 1
    
    return f"INV-{today}-{next_seq:04d}"


def calculate_due_date(issue_date, days=30):
    """
    Calculate due date for invoice (default 30 days from issue)
    """
    if isinstance(issue_date, str):
        issue_date = datetime.strptime(issue_date, "%Y-%m-%d").date()
    
    return issue_date + timedelta(days=days) 