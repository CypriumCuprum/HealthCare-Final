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