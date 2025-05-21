from django.apps import AppConfig


class EhrConfig(AppConfig):
    """Configuration for the EHR app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'EHR'
    verbose_name = 'Electronic Health Records'

    def ready(self):
        """Import signal handlers when the app is ready."""
        import EHR.signals  # noqa
