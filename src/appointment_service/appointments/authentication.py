from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
import requests
from django.conf import settings


# Hardcoded token map for development
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
            user = self.get_user_from_token(token)
            if user:
                return (user, token)
                
            # If User Service verification fails, try local verification
            if token == DEFAULT_TOKEN:
                # Return a dummy user for development
                return (CustomAnonymousUser(), token)
                    
            # Check hardcoded tokens as a fallback
            if token in TOKENS:
                # Using AnonymousUser with is_authenticated=False but with a valid token
                # The actual user ID is in TOKENS[token]
                user = CustomAnonymousUser()
                # Store the user ID as an attribute for services that need it
                user.id = TOKENS[token]
                return (user, token)
                    
            # Token not recognized
            return None
            
        except Exception as e:
            return None

    def authenticate_header(self, request):
        return 'Bearer'
        
    def get_user_from_token(self, token):
        """
        Verify token with User Service.
        """
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.post(
                f"{settings.USER_SERVICE_URL}/token/verify/",
                json={'token': token},
                headers=headers
            )
            
            if response.status_code == 200:
                # Token is valid, create a dummy user for now
                user = CustomAnonymousUser()
                user.id = response.json().get('user_id')
                return user
                
            return None
        except requests.RequestException:
            # Connection error, fall back to local verification
            return None


def verify_token(token):
    """
    Verify if a token is valid by checking with User Service.
    Returns user_id if valid, None otherwise.
    """
    try:
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