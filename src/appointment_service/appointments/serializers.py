from rest_framework import serializers

from .models import Appointment, DoctorSchedule, TimeSlot


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for the Appointment model."""
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient_id', 'doctor_id', 'appointment_time',
            'duration_minutes', 'status', 'reason_for_visit',
            'notes_doctor', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new appointment."""
    class Meta:
        model = Appointment
        fields = [
            'patient_id', 'doctor_id', 'appointment_time',
            'duration_minutes', 'reason_for_visit'
        ]


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an appointment."""
    class Meta:
        model = Appointment
        fields = [
            'status', 'notes_doctor'
        ]


class DoctorScheduleSerializer(serializers.ModelSerializer):
    """Serializer for the DoctorSchedule model."""
    class Meta:
        model = DoctorSchedule
        fields = [
            'id', 'doctor_id', 'day_of_week', 'start_time',
            'end_time', 'is_available', 'valid_from', 'valid_to',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for the TimeSlot model."""
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'doctor_id', 'start_time', 'end_time',
            'is_booked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AvailabilityRequestSerializer(serializers.Serializer):
    """Serializer for requesting doctor availability."""
    doctor_id = serializers.IntegerField()
    date = serializers.DateField()
    days_in_advance = serializers.IntegerField(
        required=False,
        default=7,
        min_value=1,
        max_value=30
    ) 