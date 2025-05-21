from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        """
        Perform initialization when the app is ready.
        This is the right place to patch models.
        """
        # Import and run our patch_user_model function
        try:
            from .authentication import patch_user_model
            patch_user_model()
        except ImportError:
            pass
