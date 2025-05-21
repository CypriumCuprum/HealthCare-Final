from django.contrib import admin
from .models import Appointment, DoctorSchedule, TimeSlot


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_id', 'doctor_id', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_time']
    search_fields = ['patient_id', 'doctor_id', 'reason_for_visit']
    date_hierarchy = 'appointment_time'
    readonly_fields = ['created_at', 'updated_at']
    fields = [
        'patient_id', 'doctor_id', 'appointment_time', 'duration_minutes',
        'status', 'reason_for_visit', 'notes_doctor', 'created_at', 'updated_at'
    ]


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor_id', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['doctor_id']
    readonly_fields = ['created_at', 'updated_at']
    fields = [
        'doctor_id', 'day_of_week', 'start_time', 'end_time',
        'is_available', 'valid_from', 'valid_to', 'created_at', 'updated_at'
    ]


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor_id', 'start_time', 'end_time', 'is_booked']
    list_filter = ['is_booked', 'start_time']
    search_fields = ['doctor_id']
    readonly_fields = ['created_at', 'updated_at']
    fields = [
        'doctor_id', 'start_time', 'end_time', 'is_booked', 'created_at', 'updated_at'
    ] 