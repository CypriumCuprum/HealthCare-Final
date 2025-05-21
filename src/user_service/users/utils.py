from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.utils.translation import gettext_lazy as _

from .models import User


# We'll import this only when needed within the method to avoid circular imports
# from .authentication import CustomAnonymousUser


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication for User model.
    """
    def get_user(self, validated_token):
        """
        Attempt to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise InvalidToken(_('User not found'), code='user_not_found')

        if not user.is_active:
            raise InvalidToken(_('User is inactive'), code='user_inactive')

        return user
        
    def authenticate(self, request):
        """
        Authenticate the request and return a tuple of (user, token).
        """
        jwt_auth = super().authenticate(request)
        if jwt_auth is None:
            # Import here to avoid circular imports
            from .authentication import CustomAnonymousUser
            # No token provided, return anonymous user
            return (CustomAnonymousUser(), None)
        
        return jwt_auth