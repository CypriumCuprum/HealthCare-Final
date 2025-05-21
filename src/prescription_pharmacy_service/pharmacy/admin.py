from django.contrib import admin
from .models import (
    Medication, Prescription, PrescriptionItem, 
    PharmacyStock, BatchExpiry, DispenseLog, DispenseItem
)

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['medication_code', 'name', 'strength', 'dosage_form', 'unit_price']
    search_fields = ['medication_code', 'name', 'generic_name']
    list_filter = ['dosage_form']


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 0


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_name', 'doctor_name', 'date_prescribed', 'status']
    list_filter = ['status', 'date_prescribed']
    search_fields = ['id', 'patient_name', 'doctor_name']
    inlines = [PrescriptionItemInline]


class BatchExpiryInline(admin.TabularInline):
    model = BatchExpiry
    extra = 0


@admin.register(PharmacyStock)
class PharmacyStockAdmin(admin.ModelAdmin):
    list_display = ['medication', 'quantity_on_hand', 'reorder_level', 'last_stocked_date']
    list_filter = ['last_stocked_date']
    inlines = [BatchExpiryInline]


class DispenseItemInline(admin.TabularInline):
    model = DispenseItem
    extra = 0


@admin.register(DispenseLog)
class DispenseLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'prescription', 'pharmacist_name', 'date_dispensed', 'payment_status']
    list_filter = ['payment_status', 'date_dispensed']
    inlines = [DispenseItemInline]
