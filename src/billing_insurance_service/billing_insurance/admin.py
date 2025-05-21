from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment, InsurancePolicy, InsuranceClaim


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ['payment_date', 'amount', 'payment_method', 'status', 'transaction_id']


class InsuranceClaimInline(admin.TabularInline):
    model = InsuranceClaim
    extra = 0
    fields = ['insurance_policy', 'submission_date', 'claim_amount', 'approved_amount', 'status']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient_id', 'issue_date', 'total_amount', 'amount_due', 'status']
    list_filter = ['status', 'issue_date']
    search_fields = ['invoice_number', 'patient_id']
    readonly_fields = ['amount_due', 'is_paid']
    inlines = [InvoiceItemInline, PaymentInline, InsuranceClaimInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('invoice_number', 'patient_id', 'issue_date', 'due_date', 'status')
        }),
        ('Financial Details', {
            'fields': ('sub_total_amount', 'tax_amount', 'discount_amount', 'total_amount', 
                      'amount_paid_by_patient', 'amount_paid_by_insurance', 'amount_due', 'is_paid')
        }),
        ('Related Records', {
            'fields': ('related_appointment_id', 'related_prescription_dispense_id', 'related_lab_order_id')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'patient_id', 'payment_date', 'amount', 'payment_method', 'status']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['invoice__invoice_number', 'patient_id', 'transaction_id']


@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ['policy_number', 'patient_id', 'provider_name', 'valid_from', 'valid_to', 'is_active', 'is_expired']
    list_filter = ['is_active', 'provider_name']
    search_fields = ['policy_number', 'patient_id', 'provider_name']
    readonly_fields = ['is_expired']


@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'insurance_policy', 'submission_date', 'claim_amount', 'approved_amount', 'status']
    list_filter = ['status', 'submission_date']
    search_fields = ['invoice__invoice_number', 'insurance_policy__policy_number']
