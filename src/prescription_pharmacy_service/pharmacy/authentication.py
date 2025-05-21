from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
import requests
from django.conf import settings


# Hardcoded token map for development - same tokens across all services
# Format: 'token': user_id
TOKENS = {
    'patient_token': 1,  # Token for a patient user (ID=1)
    'doctor_token': 2,   # Token for a doctor user (ID=2)
    'admin_token': 3,    # Token for an admin user (ID=3)
    'test_token': 1      # Another token for testing
}

# Default token that will work for any request (for development)
DEFAULT_TOKEN = 'dev_token_123456'

# Create a custom AnonymousUser
class CustomAnonymousUser(AnonymousUser):
    """Custom Anonymous User with user ID for services"""
    def __init__(self, id=None):
        super().__init__()
        self.id = id
        
    @property
    def is_authenticated(self):
        return False
    
    @property
    def is_anonymous(self):
        return True


class SimpleTokenAuthentication(BaseAuthentication):
    """
    Simple token authentication for development.
    Validates tokens with User Service.
    """
    def authenticate(self, request):
        # Extract token from Authorization header
        print(request.META)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return None
            
        try:
            # Extract the token part (remove 'Bearer ' if present)
            if ' ' in auth_header:
                _, token = auth_header.split(' ', 1)
            else:
                token = auth_header
                
            # Try to verify token with User Service
            user_id = self.verify_token(token)
            if user_id:
                user = CustomAnonymousUser(id=user_id)
                return (user, token)
                
            # Token not recognized
            return None
            
        except Exception as e:
            return None

    def authenticate_header(self, request):
        print("authenticate_header")
        return 'Bearer'
        
    def verify_token(self, token):
        """
        Verify token with User Service.
        """
        try:
            print(f"{settings.USER_SERVICE_URL}/token/verify/")
            response = requests.post(
                f"{settings.USER_SERVICE_URL}/token/verify/",
                json={'token': token}
            )
            
            if response.status_code == 200:
                return response.json().get('user_id')
                
            # If User Service is unavailable, try local verification
            if token == DEFAULT_TOKEN:
                return 1  # Default user ID
                
            if token in TOKENS:
                return TOKENS[token]
                
            return None
        except requests.RequestException:
            # Connection error, fall back to local verification
            if token == DEFAULT_TOKEN:
                return 1
                
            if token in TOKENS:
                return TOKENS[token]
                
            return None 