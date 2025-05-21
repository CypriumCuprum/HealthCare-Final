from django.db import models

# Create your models here.

class TestCatalog(models.Model):
    """Danh mục các loại xét nghiệm"""
    test_code = models.CharField(max_length=20, unique=True, help_text="Mã xét nghiệm")
    test_name = models.CharField(max_length=200, help_text="Tên xét nghiệm")
    description = models.TextField(blank=True, help_text="Mô tả xét nghiệm")
    sample_type_required = models.CharField(max_length=100, help_text="Loại mẫu cần thu thập")
    turn_around_time_hours = models.PositiveIntegerField(default=24, help_text="Thời gian hoàn thành (giờ)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Giá xét nghiệm")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test_code} - {self.test_name}"

    class Meta:
        verbose_name = "Test Catalog"
        verbose_name_plural = "Test Catalog"


class LabOrder(models.Model):
    """Phiếu yêu cầu xét nghiệm"""
    # Trạng thái của phiếu yêu cầu
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('SAMPLE_COLLECTED', 'Sample Collected'),
        ('PROCESSING', 'Processing'),
        ('RESULTS_PENDING_REVIEW', 'Results Pending Review'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Mức độ ưu tiên
    PRIORITY_CHOICES = [
        ('ROUTINE', 'Routine'),
        ('URGENT', 'Urgent'),
    ]

    # Thông tin phiếu
    patient_id = models.PositiveIntegerField(help_text="ID bệnh nhân từ User Service")
    patient_name = models.CharField(max_length=200, help_text="Tên bệnh nhân")
    doctor_id = models.PositiveIntegerField(help_text="ID bác sĩ từ User Service")
    doctor_name = models.CharField(max_length=200, help_text="Tên bác sĩ")
    ehr_encounter_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID của encounter từ EHR Service (nếu có)")
    order_date = models.DateTimeField(auto_now_add=True, help_text="Ngày tạo phiếu")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='REQUESTED', help_text="Trạng thái phiếu")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='ROUTINE', help_text="Mức độ ưu tiên")
    notes_for_lab = models.TextField(blank=True, help_text="Ghi chú cho phòng xét nghiệm")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.patient_name} - {self.status}"

    class Meta:
        verbose_name = "Lab Order"
        verbose_name_plural = "Lab Orders"


class LabOrderItem(models.Model):
    """Chi tiết các xét nghiệm trong phiếu yêu cầu"""
    # Trạng thái của từng xét nghiệm trong phiếu
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('SAMPLE_COLLECTED', 'Sample Collected'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    lab_order = models.ForeignKey(LabOrder, on_delete=models.CASCADE, related_name='items', help_text="Phiếu yêu cầu")
    test = models.ForeignKey(TestCatalog, on_delete=models.PROTECT, help_text="Xét nghiệm")
    sample_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID mẫu xét nghiệm")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='REQUESTED', help_text="Trạng thái xét nghiệm")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lab_order.id} - {self.test.test_name} - {self.status}"

    class Meta:
        verbose_name = "Lab Order Item"
        verbose_name_plural = "Lab Order Items"


class LabResult(models.Model):
    """Kết quả xét nghiệm"""
    lab_order_item = models.OneToOneField(LabOrderItem, on_delete=models.CASCADE, related_name='result', help_text="Xét nghiệm")
    technician_id = models.PositiveIntegerField(help_text="ID kỹ thuật viên từ User Service")
    technician_name = models.CharField(max_length=200, help_text="Tên kỹ thuật viên")
    result_date = models.DateTimeField(auto_now_add=True, help_text="Ngày có kết quả")
    verified_by_id = models.PositiveIntegerField(null=True, blank=True, help_text="ID người xác nhận từ User Service")
    verified_by_name = models.CharField(max_length=200, null=True, blank=True, help_text="Tên người xác nhận")
    verification_date = models.DateTimeField(null=True, blank=True, help_text="Ngày xác nhận")
    result_data = models.JSONField(default=dict, help_text="Dữ liệu kết quả dạng JSON")
    interpretation = models.TextField(blank=True, help_text="Diễn giải kết quả")
    is_abnormal = models.BooleanField(default=False, help_text="Kết quả bất thường")
    result_file_url = models.URLField(blank=True, null=True, help_text="URL file kết quả (nếu có)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result for {self.lab_order_item}"

    class Meta:
        verbose_name = "Lab Result"
        verbose_name_plural = "Lab Results"


class TestNormalRange(models.Model):
    """Định nghĩa khoảng tham chiếu cho các chỉ số xét nghiệm"""
    test = models.ForeignKey(TestCatalog, on_delete=models.CASCADE, related_name='normal_ranges', help_text="Xét nghiệm")
    parameter_name = models.CharField(max_length=100, help_text="Tên chỉ số")
    unit = models.CharField(max_length=20, help_text="Đơn vị đo")
    min_value_male = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Giá trị tối thiểu cho nam")
    max_value_male = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Giá trị tối đa cho nam")
    min_value_female = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Giá trị tối thiểu cho nữ")
    max_value_female = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Giá trị tối đa cho nữ")
    min_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Giá trị tối thiểu chung")
    max_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Giá trị tối đa chung")
    description = models.TextField(blank=True, help_text="Mô tả bổ sung")

    def __str__(self):
        return f"{self.test.test_name} - {self.parameter_name} ({self.unit})"

    class Meta:
        verbose_name = "Test Normal Range"
        verbose_name_plural = "Test Normal Ranges"
        unique_together = ('test', 'parameter_name')
