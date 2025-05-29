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

# Create user from token
class TokenUser(AnonymousUser):
    """User created from token authentication"""
    def __init__(self, id=None, role=None):
        super().__init__()
        self.id = id
        self.role = role
        
    @property
    def is_authenticated(self):
        # User từ token hợp lệ nên được coi là đã xác thực
        return True
    
    @property
    def is_anonymous(self):
        # Không còn anonymous nữa vì đã xác thực
        return False
    
    def has_role(self, role_name):
        """Check if user has specific role"""
        return self.role == role_name


class SimpleTokenAuthentication(BaseAuthentication):
    """
    Simple token authentication for development.
    Validates tokens with User Service.
    """
    def authenticate(self, request):
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(f"Received Authorization header: {auth_header}")
        
        if not auth_header:
            print("No Authorization header found")
            return None
            
        try:
            # Extract the token part (remove 'Bearer ' if present)
            if ' ' in auth_header:
                _, token = auth_header.split(' ', 1)
            else:
                token = auth_header
                
            print(f"Extracted token: {token[:10]}...")
                
            # Try to verify token with User Service
            user_data = self.verify_token(token)
            print(f"Token verification result: {user_data}")
            
            if user_data and 'user_id' in user_data:
                print(f"Token verified successfully. User data: {user_data}")
                user = TokenUser(
                    id=user_data['user_id'], 
                    role=user_data.get('role')
                )
                return (user, token)
                
            print("Token verification failed")
            return None
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None

    def authenticate_header(self, request):
        return 'Bearer'
        
    def verify_token(self, token):
        """
        Verify token with User Service.
        """
        try:
            verify_url = f"{settings.USER_SERVICE_URL}/token/verify/"
            print(f"Making request to User Service at: {verify_url}")
            print(f"Request payload: {{'token': '{token[:10]}...'}}")
            
            response = requests.post(
                verify_url,
                json={'token': token},
                timeout=5  # Add timeout to avoid hanging
            )
            
            print(f"User Service response status: {response.status_code}")
            print(f"User Service response data: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    return {
                        'user_id': data.get('user_id'),
                        'role': data.get('role')
                    }
            
            print("Token verification failed with User Service")
            return None
                
        except requests.RequestException as e:
            print(f"Error connecting to User Service: {str(e)}")
            return None 