import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .authentication import SimpleTokenAuthentication, verify_token


class CustomTokenAuthentication(BaseAuthentication):
    """
    Custom token authentication that validates tokens with User Service.
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


def notify_ehr_service(appointment_id, patient_id, doctor_id, appointment_time, token=None):
    """
    Notify EHR Service when an appointment is completed.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    data = {
        'appointment_id': appointment_id,
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'appointment_time': appointment_time
    }
    
    try:
        response = requests.post(
            f"{settings.EHR_SERVICE_URL}/ehr/internal/patients/{patient_id}/link-appointment/",
            json=data,
            headers=headers
        )
        return response.status_code == 200 or response.status_code == 201
    except requests.RequestException:
        return False


def notify_billing_service(appointment_id, patient_id, doctor_id, service_description, amount, token=None):
    """
    Notify Billing Service when an appointment is completed.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    data = {
        'appointment_id': appointment_id,
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'service_description': service_description,
        'amount': amount
    }
    
    try:
        response = requests.post(
            f"{settings.BILLING_SERVICE_URL}/billing/internal/create-invoice-for-appointment/",
            json=data,
            headers=headers
        )
        return response.status_code == 200 or response.status_code == 201
    except requests.RequestException:
        return False


def notify_notification_service(notification_type, recipient_id, data, token=None):
    """
    Send notification via Notification Service.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    notification_data = {
        'notification_type': notification_type,
        'recipient_id': recipient_id,
        'data': data
    }
    
    try:
        response = requests.post(
            f"{settings.NOTIFICATION_SERVICE_URL}/notifications/send/",
            json=notification_data,
            headers=headers
        )
        return response.status_code == 200 or response.status_code == 201
    except requests.RequestException:
        return False


def generate_time_slots(doctor_id, schedule, start_date, days=7, slot_duration=30):
    """
    Generate time slots based on doctor schedule.
    
    Args:
        doctor_id: ID of the doctor
        schedule: A DoctorSchedule instance
        start_date: Date to start generating slots from
        days: Number of days to generate slots for
        slot_duration: Duration of each slot in minutes
    
    Returns:
        List of time slot dictionaries
    """
    from .models import TimeSlot
    
    slots = []
    current_date = start_date
    end_date = start_date + timedelta(days=days)
    
    while current_date < end_date:
        # Check if this date falls within the schedule's validity period
        if (schedule.valid_from <= current_date and 
                (schedule.valid_to is None or current_date <= schedule.valid_to)):
            
            # Check if the day of week matches the schedule
            if current_date.weekday() == schedule.day_of_week:
                # Create slots for this day
                slot_start = datetime.combine(
                    current_date, 
                    schedule.start_time
                )
                slot_start = timezone.make_aware(slot_start)
                day_end = datetime.combine(
                    current_date,
                    schedule.end_time
                )
                day_end = timezone.make_aware(day_end)
                
                while slot_start + timedelta(minutes=slot_duration) <= day_end:
                    slot_end = slot_start + timedelta(minutes=slot_duration)
                    
                    # Check if slot already exists
                    if not TimeSlot.objects.filter(
                        doctor_id=doctor_id,
                        start_time=slot_start,
                        end_time=slot_end
                    ).exists():
                        # Create new slot
                        slot = TimeSlot(
                            doctor_id=doctor_id,
                            start_time=slot_start,
                            end_time=slot_end,
                            is_booked=False
                        )
                        slots.append(slot)
                    
                    # Move to next slot
                    slot_start = slot_end
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return slots 