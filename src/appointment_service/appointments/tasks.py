from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import Appointment, DoctorSchedule, TimeSlot
from .utils import notify_notification_service, notify_ehr_service, notify_billing_service, get_user_details


@shared_task
def send_appointment_notification(appointment_id, notification_type):
    """
    Send notifications related to appointment status changes.
    
    Args:
        appointment_id: ID of the appointment
        notification_type: Type of notification to send
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} not found"
    
    # Get user details for patient and doctor
    patient = get_user_details(appointment.patient_id)
    doctor = get_user_details(appointment.doctor_id)
    
    if not patient or not doctor:
        return "Failed to get user details"
    
    patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
    doctor_name = f"Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')}"
    
    # Format appointment time
    appointment_time = appointment.appointment_time.strftime("%Y-%m-%d %H:%M")
    
    # Notification data based on type
    data = {
        "appointment_id": appointment.id,
        "appointment_time": appointment_time,
        "patient_name": patient_name,
        "doctor_name": doctor_name,
        "reason_for_visit": appointment.reason_for_visit,
        "status": appointment.status
    }
    
    # Send notification based on type
    if notification_type == 'APPOINTMENT_REQUESTED_PATIENT':
        notify_notification_service(
            notification_type=notification_type,
            recipient_id=appointment.patient_id,
            data=data
        )
    elif notification_type == 'APPOINTMENT_REQUESTED_DOCTOR':
        notify_notification_service(
            notification_type=notification_type,
            recipient_id=appointment.doctor_id,
            data=data
        )
    elif notification_type == 'APPOINTMENT_CONFIRMED_PATIENT':
        notify_notification_service(
            notification_type=notification_type,
            recipient_id=appointment.patient_id,
            data=data
        )
    elif notification_type == 'APPOINTMENT_CANCELLED':
        # Notify both patient and doctor
        notify_notification_service(
            notification_type=notification_type,
            recipient_id=appointment.patient_id,
            data=data
        )
        notify_notification_service(
            notification_type=notification_type,
            recipient_id=appointment.doctor_id,
            data=data
        )
    elif notification_type == 'APPOINTMENT_REMINDER_PATIENT':
        notify_notification_service(
            notification_type=notification_type,
            recipient_id=appointment.patient_id,
            data=data
        )
    elif notification_type == 'APPOINTMENT_REMINDER_DOCTOR':
        notify_notification_service(
            notification_type=notification_type,
            recipient_id=appointment.doctor_id,
            data=data
        )
    
    return f"Notification {notification_type} sent successfully"


@shared_task
def send_appointment_reminders():
    """
    Send reminders for upcoming appointments.
    Schedule this task to run daily.
    """
    # Get appointments in the next 24 hours
    reminder_time = timezone.now() + timedelta(hours=24)
    appointments = Appointment.objects.filter(
        appointment_time__lte=reminder_time,
        appointment_time__gte=timezone.now(),
        status=Appointment.CONFIRMED
    )
    
    for appointment in appointments:
        send_appointment_notification.delay(
            appointment.id,
            'APPOINTMENT_REMINDER_PATIENT'
        )
        send_appointment_notification.delay(
            appointment.id,
            'APPOINTMENT_REMINDER_DOCTOR'
        )
    
    return f"Sent reminders for {appointments.count()} appointments"


@shared_task
def process_completed_appointment(appointment_id, token=None):
    """
    Process a completed appointment:
    1. Notify EHR service to create an encounter
    2. Notify Billing service to create an invoice
    
    Args:
        appointment_id: ID of the completed appointment
        token: Authentication token for API calls
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} not found"
    
    if appointment.status != Appointment.COMPLETED:
        return f"Appointment {appointment_id} is not completed"
    
    # Notify EHR service
    ehr_result = notify_ehr_service(
        appointment_id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_time=appointment.appointment_time.isoformat(),
        token=token
    )
    
    # Notify Billing service (fixed cost of $100 for consultation)
    billing_result = notify_billing_service(
        appointment_id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        service_description="Medical Consultation",
        amount=100.00,
        token=token
    )
    
    return {
        "ehr_notification": "success" if ehr_result else "failed",
        "billing_notification": "success" if billing_result else "failed"
    }


@shared_task
def generate_timeslots_for_doctor(doctor_id, start_date=None, days=30):
    """
    Generate time slots for a doctor based on their schedule.
    
    Args:
        doctor_id: ID of the doctor
        start_date: Start date for generating slots (defaults to today)
        days: Number of days to generate slots for
    """
    from .utils import generate_time_slots
    
    if start_date is None:
        start_date = timezone.now().date()
    else:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    
    # Get doctor's schedule
    schedules = DoctorSchedule.objects.filter(
        doctor_id=doctor_id,
        is_available=True,
        valid_from__lte=start_date + timedelta(days=days),
        valid_to__isnull=True
    ).order_by('day_of_week')
    
    # Add schedules with specific end dates that are still valid
    schedules = schedules | DoctorSchedule.objects.filter(
        doctor_id=doctor_id,
        is_available=True,
        valid_from__lte=start_date + timedelta(days=days),
        valid_to__gte=start_date
    ).order_by('day_of_week')
    
    total_slots = 0
    
    # Generate slots for each schedule
    for schedule in schedules:
        slots = generate_time_slots(
            doctor_id=doctor_id,
            schedule=schedule,
            start_date=start_date,
            days=days
        )
        
        # Save slots to database
        if slots:
            TimeSlot.objects.bulk_create(slots)
            total_slots += len(slots)
    
    return f"Generated {total_slots} time slots for doctor {doctor_id}" 