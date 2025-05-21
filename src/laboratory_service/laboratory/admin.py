from django.contrib import admin
from .models import TestCatalog, LabOrder, LabOrderItem, LabResult, TestNormalRange


class TestNormalRangeInline(admin.TabularInline):
    model = TestNormalRange
    extra = 1


@admin.register(TestCatalog)
class TestCatalogAdmin(admin.ModelAdmin):
    list_display = ('test_code', 'test_name', 'sample_type_required', 'price', 'turn_around_time_hours')
    search_fields = ('test_code', 'test_name')
    list_filter = ('sample_type_required',)
    inlines = [TestNormalRangeInline]


class LabOrderItemInline(admin.TabularInline):
    model = LabOrderItem
    extra = 1
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_name', 'doctor_name', 'status', 'priority', 'order_date')
    list_filter = ('status', 'priority', 'order_date')
    search_fields = ('patient_name', 'doctor_name', 'id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LabOrderItemInline]


@admin.register(LabOrderItem)
class LabOrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_lab_order_id', 'get_test_name', 'status', 'sample_id')
    list_filter = ('status',)
    search_fields = ('lab_order__patient_name', 'test__test_name', 'sample_id')
    readonly_fields = ('created_at', 'updated_at')

    def get_lab_order_id(self, obj):
        return obj.lab_order.id
    get_lab_order_id.short_description = 'Lab Order ID'
    get_lab_order_id.admin_order_field = 'lab_order__id'

    def get_test_name(self, obj):
        return obj.test.test_name
    get_test_name.short_description = 'Test Name'
    get_test_name.admin_order_field = 'test__test_name'


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_lab_order_id', 'get_test_name', 'technician_name', 'result_date', 'is_abnormal')
    list_filter = ('is_abnormal', 'result_date')
    search_fields = ('lab_order_item__lab_order__patient_name', 'technician_name')
    readonly_fields = ('created_at', 'updated_at')

    def get_lab_order_id(self, obj):
        return obj.lab_order_item.lab_order.id
    get_lab_order_id.short_description = 'Lab Order ID'
    get_lab_order_id.admin_order_field = 'lab_order_item__lab_order__id'

    def get_test_name(self, obj):
        return obj.lab_order_item.test.test_name
    get_test_name.short_description = 'Test Name'
    get_test_name.admin_order_field = 'lab_order_item__test__test_name'


@admin.register(TestNormalRange)
class TestNormalRangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_test_name', 'parameter_name', 'unit')
    search_fields = ('test__test_name', 'parameter_name')
    list_filter = ('test__test_name',)

    def get_test_name(self, obj):
        return obj.test.test_name
    get_test_name.short_description = 'Test Name'
    get_test_name.admin_order_field = 'test__test_name'
