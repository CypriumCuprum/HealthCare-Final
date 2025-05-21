from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment, InsurancePolicy, InsuranceClaim


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'item_type', 'description', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['total_price']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_date', 'amount', 'payment_method', 
                  'transaction_id', 'status', 'notes']
        read_only_fields = ['id', 'payment_date']


class InsuranceClaimSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='insurance_policy.provider_name', read_only=True)
    
    class Meta:
        model = InsuranceClaim
        fields = ['id', 'insurance_policy', 'provider_name', 'submission_date', 
                 'claim_amount', 'approved_amount', 'rejected_amount', 
                 'status', 'insurer_notes', 'hospital_notes', 'claim_reference_number']
        read_only_fields = ['id', 'submission_date']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, required=False)
    payments = PaymentSerializer(many=True, read_only=True)
    claims = InsuranceClaimSerializer(many=True, read_only=True)
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'patient_id', 'invoice_number', 'issue_date', 'due_date',
                 'sub_total_amount', 'tax_amount', 'discount_amount', 'total_amount',
                 'amount_paid_by_patient', 'amount_paid_by_insurance', 'amount_due', 'is_paid',
                 'status', 'related_appointment_id', 'related_prescription_dispense_id',
                 'related_lab_order_id', 'items', 'payments', 'claims', 'created_at', 'updated_at']
        read_only_fields = ['id', 'invoice_number', 'amount_paid_by_patient', 
                           'amount_paid_by_insurance', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        # Generate invoice number - simple implementation
        last_invoice = Invoice.objects.order_by('-id').first()
        invoice_num = f"INV-{last_invoice.id + 1:06d}" if last_invoice else "INV-000001"
        
        invoice = Invoice.objects.create(invoice_number=invoice_num, **validated_data)
        
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        return invoice


class InsurancePolicySerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = InsurancePolicy
        fields = ['id', 'patient_id', 'insurance_provider_id', 'provider_name',
                 'policy_number', 'member_id', 'valid_from', 'valid_to',
                 'coverage_details_json', 'is_active', 'is_expired',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoicePaymentSerializer(serializers.Serializer):
    """Serializer for making a payment on an invoice"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    transaction_id = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class CreateInvoiceForAppointmentSerializer(serializers.Serializer):
    """Serializer for creating invoice from appointment"""
    appointment_id = serializers.IntegerField()
    patient_id = serializers.IntegerField()
    doctor_id = serializers.IntegerField()
    service_description = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class CreateInvoiceForMedicationSerializer(serializers.Serializer):
    """Serializer for creating invoice from medication dispense"""
    dispense_log_id = serializers.CharField()
    patient_id = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField()
    )


class CreateInvoiceForLabTestSerializer(serializers.Serializer):
    """Serializer for creating invoice from lab test"""
    lab_order_id = serializers.CharField()
    patient_id = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField()
    ) 