from rest_framework import serializers
from .models import (
    Medication, Prescription, PrescriptionItem, 
    PharmacyStock, BatchExpiry, DispenseLog, DispenseItem
)


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'


class BatchExpirySerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchExpiry
        fields = '__all__'


class PharmacyStockSerializer(serializers.ModelSerializer):
    batches = BatchExpirySerializer(many=True, read_only=True)
    medication_name = serializers.CharField(source='medication.name', read_only=True)

    class Meta:
        model = PharmacyStock
        fields = '__all__'


class PrescriptionItemSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    medication_dosage_form = serializers.CharField(source='medication.dosage_form', read_only=True)
    medication_strength = serializers.CharField(source='medication.strength', read_only=True)

    class Meta:
        model = PrescriptionItem
        fields = [
            'id', 'medication', 'medication_name', 'medication_dosage_form', 
            'medication_strength', 'dosage', 'frequency', 'duration_days', 
            'instructions', 'quantity_prescribed', 'quantity_dispensed'
        ]
        read_only_fields = ['quantity_dispensed']


class DispenseItemSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)

    class Meta:
        model = DispenseItem
        fields = '__all__'


class DispenseLogSerializer(serializers.ModelSerializer):
    items = DispenseItemSerializer(many=True, read_only=True)

    class Meta:
        model = DispenseLog
        fields = '__all__'
        read_only_fields = ['date_dispensed']


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True)
    dispense_logs = DispenseLogSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'patient_id', 'patient_name', 'doctor_id', 'doctor_name',
            'ehr_encounter_id', 'date_prescribed', 'status', 
            'notes_for_pharmacist', 'items', 'dispense_logs',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        prescription = Prescription.objects.create(**validated_data)
        
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)
            
        return prescription


class PrescriptionDispenseSerializer(serializers.Serializer):
    pharmacist_id = serializers.IntegerField()
    pharmacist_name = serializers.CharField()
    items_dispensed = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            allow_empty=False
        )
    )
    notes = serializers.CharField(required=False, allow_blank=True)


class MedicationStockUpdateSerializer(serializers.Serializer):
    quantity_to_add = serializers.IntegerField(min_value=1)
    batch_number = serializers.CharField()
    expiry_date = serializers.DateField() 