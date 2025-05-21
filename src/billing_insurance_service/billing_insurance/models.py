from django.db import models
from django.utils import timezone


class Invoice(models.Model):
    """Model representing an invoice for a patient"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_PATIENT', 'Pending Patient Payment'),
        ('PENDING_INSURANCE', 'Pending Insurance Payment'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
        ('WRITTEN_OFF', 'Written Off'),
    ]
    
    patient_id = models.IntegerField(help_text="ID of the patient from User Service")
    invoice_number = models.CharField(max_length=50, unique=True, help_text="Unique invoice number")
    issue_date = models.DateField(default=timezone.now, help_text="Date invoice was issued")
    due_date = models.DateField(help_text="Date payment is due")
    sub_total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Subtotal amount before tax/discount")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Tax amount")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Discount amount")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount after tax and discount")
    amount_paid_by_patient = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Amount paid by patient")
    amount_paid_by_insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Amount paid by insurance")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', help_text="Current status of invoice")
    related_appointment_id = models.IntegerField(null=True, blank=True, help_text="ID of related appointment, if any")
    related_prescription_dispense_id = models.CharField(max_length=50, null=True, blank=True, help_text="ID of related prescription dispense, if any")
    related_lab_order_id = models.CharField(max_length=50, null=True, blank=True, help_text="ID of related lab order, if any")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def amount_due(self):
        """Calculate remaining amount due"""
        return max(0, self.total_amount - self.amount_paid_by_patient - self.amount_paid_by_insurance)
    
    @property
    def is_paid(self):
        """Check if invoice is fully paid"""
        return self.amount_due == 0
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.status}"


class InvoiceItem(models.Model):
    """Model representing an individual line item on an invoice"""
    ITEM_TYPE_CHOICES = [
        ('CONSULTATION', 'Consultation'),
        ('MEDICATION', 'Medication'),
        ('LAB_TEST', 'Laboratory Test'),
        ('OTHER_SERVICE', 'Other Service'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=50, choices=ITEM_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="quantity * unit_price")
    
    def save(self, *args, **kwargs):
        """Auto-calculate total price before saving"""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.description} - {self.total_price}"


class Payment(models.Model):
    """Model representing a payment transaction for an invoice"""
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('CASH', 'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('INSURANCE_PAYOUT', 'Insurance Payout'),
        ('VOUCHER', 'Voucher'),
    ]
    
    STATUS_CHOICES = [
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
        ('REFUNDED', 'Refunded'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    patient_id = models.IntegerField(help_text="ID of the patient from User Service")
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, null=True, blank=True, help_text="External transaction ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        invoice_num = self.invoice.invoice_number if self.invoice else "No Invoice"
        return f"Payment {self.id} - {self.amount} - {invoice_num}"


class InsurancePolicy(models.Model):
    """Model representing a patient's insurance policy"""
    patient_id = models.IntegerField(help_text="ID of the patient from User Service")
    insurance_provider_id = models.IntegerField(null=True, blank=True, help_text="ID of insurance provider from User Service")
    provider_name = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=100, unique=True)
    member_id = models.CharField(max_length=100)
    valid_from = models.DateField()
    valid_to = models.DateField()
    coverage_details_json = models.JSONField(default=dict, blank=True, help_text="Insurance coverage details")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_expired(self):
        """Check if policy is expired"""
        return timezone.now().date() > self.valid_to
    
    def __str__(self):
        return f"Policy {self.policy_number} - {self.provider_name}"


class InsuranceClaim(models.Model):
    """Model representing an insurance claim for an invoice"""
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('PROCESSING', 'Processing'),
        ('AWAITING_DOCUMENTS', 'Awaiting Documents'),
        ('APPROVED', 'Approved'),
        ('PARTIALLY_APPROVED', 'Partially Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID_BY_INSURER', 'Paid by Insurer'),
        ('CLOSED', 'Closed'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='claims')
    insurance_policy = models.ForeignKey(InsurancePolicy, on_delete=models.PROTECT, related_name='claims')
    submission_date = models.DateField(default=timezone.now)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount claimed from insurance")
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rejected_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED')
    insurer_notes = models.TextField(blank=True, help_text="Notes from insurance provider")
    hospital_notes = models.TextField(blank=True, help_text="Notes from hospital staff")
    claim_reference_number = models.CharField(max_length=100, null=True, blank=True, help_text="External reference number")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Claim {self.id} - {self.insurance_policy.provider_name} - {self.status}"
