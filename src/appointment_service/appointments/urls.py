from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AppointmentViewSet,
    DoctorScheduleViewSet,
    TimeSlotViewSet,
    DoctorAvailabilityView
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'doctor-schedules', DoctorScheduleViewSet, basename='doctorschedule')
router.register(r'time-slots', TimeSlotViewSet, basename='timeslot')

urlpatterns = [
    path('', include(router.urls)),
    
    # Patient endpoints
    path('patients/<int:patient_id>/appointments/', 
        AppointmentViewSet.as_view({'get': 'list'}), 
        {'patient_id': True}, 
        name='patient-appointments'),
    
    # Doctor endpoints
    path('doctors/<int:doctor_id>/appointments/', 
        AppointmentViewSet.as_view({'get': 'list'}), 
        {'doctor_id': True}, 
        name='doctor-appointments'),
    path('doctors/<int:doctor_id>/schedules/', 
        DoctorScheduleViewSet.as_view({'get': 'list'}), 
        {'doctor_id': True}, 
        name='doctor-schedules'),
    
    # Availability endpoint
    path('doctors/availability/', 
        DoctorAvailabilityView.as_view(), 
        name='doctor-availability'),
] 