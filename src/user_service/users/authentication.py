from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from django.middleware.csrf import CsrfViewMiddleware


# Create a custom AnonymousUser that mimics Django's auth system
class CustomAnonymousUser(AnonymousUser):
    @property
    def is_authenticated(self):
        return False


# Function to patch User model with authentication properties
# Will be called later to avoid circular imports
def patch_user_model():
    from .models import User
    
    if not hasattr(User, 'is_authenticated'):
        def get_is_authenticated(self):
            """
            Always return True. This is a way to tell if the user has been
            authenticated in templates.
            """
            return True
        
        User.is_authenticated = property(get_is_authenticated)
    
    if not hasattr(User, 'is_anonymous'):
        def get_is_anonymous(self):
            """
            Always return False. This is a way to tell if the user has been
            not authenticated in templates.
            """
            return False
        
        User.is_anonymous = property(get_is_anonymous)


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication for handling token validation.
    """
    def authenticate(self, request):
        from .utils import CustomJWTAuthentication
        
        jwt_authenticator = CustomJWTAuthentication()
        
        try:
            result = jwt_authenticator.authenticate(request)
            if result is not None:
                user, token = result
                return (user, token)
        except Exception as e:
            raise AuthenticationFailed(str(e))
        
        return None

    def authenticate_header(self, request):
        return 'Bearer'


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user.
    """
    refresh = RefreshToken.for_user(user)
    
    # Chỉ thêm role vào token payload
    refresh['role'] = user.role.name if user.role else None
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }