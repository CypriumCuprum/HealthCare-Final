from django.db import models
from django.utils.translation import gettext_lazy as _


class Appointment(models.Model):
    """Model for storing appointments."""
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CANCELLED_PATIENT = 'CANCELLED_PATIENT'
    CANCELLED_DOCTOR = 'CANCELLED_DOCTOR'
    COMPLETED = 'COMPLETED'
    NO_SHOW = 'NO_SHOW'

    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (CONFIRMED, _('Confirmed')),
        (CANCELLED_PATIENT, _('Cancelled by Patient')),
        (CANCELLED_DOCTOR, _('Cancelled by Doctor')),
        (COMPLETED, _('Completed')),
        (NO_SHOW, _('No Show')),
    ]

    patient_id = models.IntegerField(
        _('Patient ID'),
        help_text=_('ID from User Service')
    )
    doctor_id = models.IntegerField(
        _('Doctor ID'),
        help_text=_('ID from User Service')
    )
    appointment_time = models.DateTimeField(
        _('Appointment Time')
    )
    duration_minutes = models.IntegerField(
        _('Duration (minutes)'),
        default=30
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    reason_for_visit = models.TextField(
        _('Reason for Visit'),
        blank=True
    )
    notes_doctor = models.TextField(
        _('Doctor Notes'),
        blank=True
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['doctor_id']),
            models.Index(fields=['appointment_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Appointment {self.id} - {self.appointment_time}"


class DoctorSchedule(models.Model):
    """Model for storing doctor schedules."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    DAY_CHOICES = [
        (MONDAY, _('Monday')),
        (TUESDAY, _('Tuesday')),
        (WEDNESDAY, _('Wednesday')),
        (THURSDAY, _('Thursday')),
        (FRIDAY, _('Friday')),
        (SATURDAY, _('Saturday')),
        (SUNDAY, _('Sunday')),
    ]

    doctor_id = models.IntegerField(
        _('Doctor ID'),
        help_text=_('ID from User Service')
    )
    day_of_week = models.IntegerField(
        _('Day of Week'),
        choices=DAY_CHOICES
    )
    start_time = models.TimeField(
        _('Start Time')
    )
    end_time = models.TimeField(
        _('End Time')
    )
    is_available = models.BooleanField(
        _('Is Available'),
        default=True
    )
    valid_from = models.DateField(
        _('Valid From')
    )
    valid_to = models.DateField(
        _('Valid To'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Doctor Schedule')
        verbose_name_plural = _('Doctor Schedules')
        indexes = [
            models.Index(fields=['doctor_id']),
            models.Index(fields=['day_of_week']),
            models.Index(fields=['valid_from', 'valid_to']),
        ]

    def __str__(self):
        return f"Schedule for Doctor {self.doctor_id} - {self.get_day_of_week_display()}"


class TimeSlot(models.Model):
    """Model for storing available time slots."""
    doctor_id = models.IntegerField(
        _('Doctor ID'),
        help_text=_('ID from User Service')
    )
    start_time = models.DateTimeField(
        _('Start Time')
    )
    end_time = models.DateTimeField(
        _('End Time')
    )
    is_booked = models.BooleanField(
        _('Is Booked'),
        default=False
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Time Slot')
        verbose_name_plural = _('Time Slots')
        indexes = [
            models.Index(fields=['doctor_id']),
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['is_booked']),
        ]

    def __str__(self):
        return f"Time Slot {self.start_time} - {self.end_time}" 