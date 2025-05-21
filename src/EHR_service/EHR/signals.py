from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Encounter, MedicalRecord


@receiver(post_save, sender=MedicalRecord)
def medical_record_post_save(sender, instance, created, **kwargs):
    """Signal handler for MedicalRecord post_save."""
    if created:
        # Add any initialization logic for new medical records
        pass


@receiver(post_save, sender=Encounter)
def encounter_post_save(sender, instance, created, **kwargs):
    """Signal handler for Encounter post_save."""
    if created:
        # Add any initialization logic for new encounters
        pass 