from rest_framework import serializers
from .models import TestCatalog, LabOrder, LabOrderItem, LabResult, TestNormalRange


class TestNormalRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestNormalRange
        fields = '__all__'


class TestCatalogSerializer(serializers.ModelSerializer):
    normal_ranges = TestNormalRangeSerializer(many=True, read_only=True)
    
    class Meta:
        model = TestCatalog
        fields = '__all__'


class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = '__all__'


class LabOrderItemSerializer(serializers.ModelSerializer):
    test = TestCatalogSerializer(read_only=True)
    test_id = serializers.PrimaryKeyRelatedField(
        queryset=TestCatalog.objects.all(),
        source='test',
        write_only=True
    )
    result = LabResultSerializer(read_only=True)
    
    class Meta:
        model = LabOrderItem
        fields = [
            'id', 'lab_order', 'test', 'test_id', 'sample_id', 
            'status', 'result', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        return LabOrderItem.objects.create(**validated_data)


class LabOrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = LabOrder
        fields = [
            'patient_id', 'patient_name', 'doctor_id', 'doctor_name',
            'ehr_encounter_id', 'priority', 'notes_for_lab', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        lab_order = LabOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            test_id = item_data.pop('test_id')
            LabOrderItem.objects.create(
                lab_order=lab_order,
                test_id=test_id,
                **item_data
            )
        
        return lab_order


class LabOrderSerializer(serializers.ModelSerializer):
    items = LabOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = LabOrder
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class LabResultCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = [
            'lab_order_item', 'technician_id', 'technician_name',
            'verified_by_id', 'verified_by_name', 'verification_date',
            'result_data', 'interpretation', 'is_abnormal', 'result_file_url'
        ]
    
    def create(self, validated_data):
        lab_result = LabResult.objects.create(**validated_data)
        
        # Cập nhật trạng thái của LabOrderItem thành COMPLETED
        lab_order_item = lab_result.lab_order_item
        lab_order_item.status = 'COMPLETED'
        lab_order_item.save()
        
        # Kiểm tra xem tất cả các item của LabOrder đã hoàn thành chưa
        lab_order = lab_order_item.lab_order
        all_items_completed = all(
            item.status == 'COMPLETED' 
            for item in lab_order.items.all()
        )
        
        # Nếu tất cả đã hoàn thành, cập nhật trạng thái LabOrder
        if all_items_completed:
            lab_order.status = 'COMPLETED'
            lab_order.save()
        
        return lab_result 