import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication

from .authentication import SimpleTokenAuthentication


class CustomTokenAuthentication(BaseAuthentication):
    """
    Custom token authentication for Notification Service.
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


def get_user_contact_info(user_id, token=None):
    """
    Get user contact information for sending notifications.
    """
    user = get_user_details(user_id, token)
    if not user:
        return None
        
    return {
        'email': user.get('email'),
        'phone_number': user.get('phone_number'),
        'name': f"{user.get('first_name', '')} {user.get('last_name', '')}"
    }


def send_email(to_email, subject, content, is_html=False):
    """
    Send email via email provider/service.
    Placeholder for actual email sending implementation.
    """
    # In a real implementation, would use Django's send_mail or an external service like SendGrid
    # For development, just log the email
    print(f"Email sent to {to_email}: {subject}")
    return True


def send_sms(to_phone_number, message):
    """
    Send SMS via SMS provider service.
    Placeholder for actual SMS sending implementation.
    """
    # In a real implementation, would use a service like Twilio
    # For development, just log the SMS
    print(f"SMS sent to {to_phone_number}: {message[:30]}...")
    return True 