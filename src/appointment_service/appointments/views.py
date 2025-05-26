from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from .models import Appointment, DoctorSchedule, TimeSlot
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AppointmentUpdateSerializer,
    AvailabilityRequestSerializer,
    DoctorScheduleSerializer,
    TimeSlotSerializer,
)
from .tasks import (
    send_appointment_notification,
    process_completed_appointment,
    generate_timeslots_for_doctor
)
from .utils import get_user_details, generate_time_slots


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing appointments."""
    queryset = Appointment.objects.all().order_by('-appointment_time')
    serializer_class = AppointmentSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AppointmentUpdateSerializer
        return self.serializer_class

    def get_queryset(self):
        """Filter appointments based on query parameters."""
        queryset = self.queryset
        
        # Filter by patient_id if provided
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
            
        # Filter by doctor_id if provided
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
            
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_time__date__gte=start)
            except ValueError:
                pass
                
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_time__date__lte=end)
            except ValueError:
                pass
                
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        """Create appointment, update time slot, and send notifications."""
        # Get time slot if available
        appointment_time = serializer.validated_data.get('appointment_time')
        doctor_id = serializer.validated_data.get('doctor_id')
        duration_minutes = serializer.validated_data.get('duration_minutes', 30)
        
        if appointment_time and doctor_id:
            # Check for time slot availability
            end_time = appointment_time + timedelta(minutes=duration_minutes)
            try:
                time_slot = TimeSlot.objects.get(
                    doctor_id=doctor_id,
                    start_time=appointment_time,
                    end_time=end_time,
                    is_booked=False
                )
                # Mark the time slot as booked
                time_slot.is_booked = True
                time_slot.save()
            except TimeSlot.DoesNotExist:
                # Create a time slot if it doesn't exist (for flexibility)
                time_slot = TimeSlot.objects.create(
                    doctor_id=doctor_id,
                    start_time=appointment_time,
                    end_time=end_time,
                    is_booked=True
                )
        
        # Save the appointment
        appointment = serializer.save()
        
        # Send notifications
        send_appointment_notification(
            appointment.id,
            'APPOINTMENT_REQUESTED_PATIENT'
        )
        send_appointment_notification(
            appointment.id,
            'APPOINTMENT_REQUESTED_DOCTOR'
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment."""
        appointment = self.get_object()
        if appointment.status != Appointment.PENDING:
            return Response(
                {'error': 'Only pending appointments can be confirmed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = Appointment.CONFIRMED
        appointment.save()
        
        # Send notification to patient
        send_appointment_notification(
            appointment.id,
            'APPOINTMENT_CONFIRMED_PATIENT'
        )
        
        return Response({'status': 'confirmed'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark an appointment as completed and process follow-up actions."""
        appointment = self.get_object()
        if appointment.status != Appointment.CONFIRMED:
            return Response(
                {'error': 'Only confirmed appointments can be completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = Appointment.COMPLETED
        appointment.save()
        
        # Process the completed appointment (notify EHR and Billing)
        process_completed_appointment(
            appointment.id,
            token=request.auth
        )
        
        return Response({'status': 'completed'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment."""
        appointment = self.get_object()
        if appointment.status not in [Appointment.PENDING, Appointment.CONFIRMED]:
            return Response(
                {'error': 'Only pending or confirmed appointments can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Determine who is canceling the appointment
        cancel_type = request.data.get('cancel_type', 'PATIENT')
        
        if cancel_type.upper() == 'PATIENT':
            appointment.status = Appointment.CANCELLED_PATIENT
        else:
            appointment.status = Appointment.CANCELLED_DOCTOR
            
        appointment.save()
        
        # Free up the time slot
        try:
            time_slot = TimeSlot.objects.get(
                doctor_id=appointment.doctor_id,
                start_time=appointment.appointment_time,
                end_time=appointment.appointment_time + timedelta(minutes=appointment.duration_minutes)
            )
            time_slot.is_booked = False
            time_slot.save()
        except TimeSlot.DoesNotExist:
            pass
        
        # Send cancellation notification
        send_appointment_notification(
            appointment.id,
            'APPOINTMENT_CANCELLED'
        )
        
        return Response({'status': 'cancelled'})


class DoctorScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing doctor schedules."""
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleSerializer
    
    def get_queryset(self):
        """Filter schedules based on query parameters."""
        queryset = self.queryset
        
        # Filter by doctor_id if provided
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
            
        # Filter by is_available if provided
        is_available = self.request.query_params.get('is_available')
        if is_available is not None:
            is_available = is_available.lower() == 'true'
            queryset = queryset.filter(is_available=is_available)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def generate_slots(self, request):
        """Generate time slots based on doctor schedules."""
        doctor_id = request.data.get('doctor_id')
        days = request.data.get('days', 30)
        start_date_str = request.data.get('start_date')
        
        if not doctor_id:
            return Response(
                {'error': 'Doctor ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Convert start_date if provided
        start_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        # Start background task to generate slots
        task = generate_timeslots_for_doctor(
            doctor_id=doctor_id,
            start_date=start_date_str if start_date_str else None,
            days=days
        )
        
        return Response({
            'status': 'processing',
            'message': f'Generating time slots for doctor {doctor_id}',
            'task_id': task.id
        })


class TimeSlotViewSet(viewsets.ModelViewSet):
    """ViewSet for managing time slots."""
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    
    def get_queryset(self):
        """Filter time slots based on query parameters."""
        queryset = self.queryset
        
        # Filter by doctor_id if provided
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
            
        # Filter by is_booked if provided
        is_booked = self.request.query_params.get('is_booked')
        if is_booked is not None:
            is_booked = is_booked.lower() == 'true'
            queryset = queryset.filter(is_booked=is_booked)
            
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date__gte=start)
            except ValueError:
                pass
                
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(end_time__date__lte=end)
            except ValueError:
                pass
                
        return queryset.order_by('start_time')


class DoctorAvailabilityView(APIView):
    """API for checking doctor availability."""
    def post(self, request):
        """Check doctor availability for a given date range."""
        serializer = AvailabilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        doctor_id = serializer.validated_data['doctor_id']
        start_date = serializer.validated_data['date']
        days_in_advance = serializer.validated_data['days_in_advance']
        end_date = start_date + timedelta(days=days_in_advance)
        
        # Get all available time slots for the date range
        available_slots = TimeSlot.objects.filter(
            doctor_id=doctor_id,
            start_time__date__gte=start_date,
            end_time__date__lte=end_date,
            is_booked=False
        ).order_by('start_time')
        
        # Get doctor details
        doctor = get_user_details(doctor_id)
        doctor_name = "Unknown Doctor"
        if doctor:
            doctor_name = f"Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')}"
        
        # Group slots by date for easier frontend display
        slots_by_date = {}
        for slot in available_slots:
            date_key = slot.start_time.date().isoformat()
            if date_key not in slots_by_date:
                slots_by_date[date_key] = []
                
            slots_by_date[date_key].append({
                'id': slot.id,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'duration_minutes': (slot.end_time - slot.start_time).seconds // 60
            })
            
        return Response({
            'doctor_id': doctor_id,
            'doctor_name': doctor_name,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'availability': slots_by_date
        }) 