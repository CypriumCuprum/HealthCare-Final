from django.db import models
from django.utils import timezone


class Medication(models.Model):
    """Danh mục thuốc"""
    medication_code = models.CharField(max_length=50, unique=True, help_text="Mã thuốc")
    name = models.CharField(max_length=255, help_text="Tên thuốc")
    generic_name = models.CharField(max_length=255, blank=True, help_text="Tên generic")
    manufacturer = models.CharField(max_length=255, blank=True, help_text="Nhà sản xuất")
    description = models.TextField(blank=True, help_text="Mô tả thuốc")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Giá tham khảo")
    dosage_form = models.CharField(max_length=100, help_text="Dạng bào chế (viên, ống, v.v.)")
    strength = models.CharField(max_length=100, help_text="Nồng độ/Hàm lượng")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medication_code} - {self.name} {self.strength}"

    class Meta:
        verbose_name = "Medication"
        verbose_name_plural = "Medications"


class Prescription(models.Model):
    """Đơn thuốc"""
    STATUS_CHOICES = [
        ('PENDING_VERIFICATION', 'Pending Verification'),
        ('VERIFIED', 'Verified'),
        ('DISPENSED_PARTIAL', 'Dispensed Partial'),
        ('DISPENSED_FULL', 'Dispensed Full'),
        ('CANCELLED', 'Cancelled'),
    ]

    patient_id = models.PositiveIntegerField(help_text="ID bệnh nhân từ User Service")
    patient_name = models.CharField(max_length=255, help_text="Tên bệnh nhân")
    doctor_id = models.PositiveIntegerField(help_text="ID bác sĩ từ User Service")
    doctor_name = models.CharField(max_length=255, help_text="Tên bác sĩ")
    ehr_encounter_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID của encounter từ EHR Service (nếu có)")
    date_prescribed = models.DateTimeField(default=timezone.now, help_text="Ngày kê đơn")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING_VERIFICATION', help_text="Trạng thái đơn thuốc")
    notes_for_pharmacist = models.TextField(blank=True, help_text="Ghi chú cho dược sĩ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription {self.id} - {self.patient_name} - {self.status}"

    class Meta:
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"


class PrescriptionItem(models.Model):
    """Chi tiết đơn thuốc"""
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items', help_text="Đơn thuốc")
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, help_text="Thuốc")
    dosage = models.CharField(max_length=100, help_text="Liều dùng (ví dụ: 1 viên)")
    frequency = models.CharField(max_length=100, help_text="Tần suất (ví dụ: 3 lần/ngày)")
    duration_days = models.PositiveIntegerField(help_text="Thời gian dùng (ngày)")
    instructions = models.TextField(blank=True, help_text="Hướng dẫn sử dụng")
    quantity_prescribed = models.PositiveIntegerField(help_text="Số lượng kê đơn")
    quantity_dispensed = models.PositiveIntegerField(default=0, help_text="Số lượng đã cấp phát")
    
    def __str__(self):
        return f"{self.prescription.id} - {self.medication.name} - {self.quantity_prescribed}"

    class Meta:
        verbose_name = "Prescription Item"
        verbose_name_plural = "Prescription Items"


class PharmacyStock(models.Model):
    """Quản lý kho thuốc"""
    medication = models.OneToOneField(Medication, on_delete=models.CASCADE, related_name='stock', help_text="Thuốc")
    quantity_on_hand = models.PositiveIntegerField(default=0, help_text="Số lượng hiện có")
    reorder_level = models.PositiveIntegerField(default=10, help_text="Mức cần đặt lại")
    last_stocked_date = models.DateTimeField(null=True, blank=True, help_text="Ngày nhập kho gần nhất")
    
    def __str__(self):
        return f"{self.medication.name} - {self.quantity_on_hand} in stock"

    class Meta:
        verbose_name = "Pharmacy Stock"
        verbose_name_plural = "Pharmacy Stocks"


class BatchExpiry(models.Model):
    """Quản lý hạn sử dụng theo lô thuốc"""
    pharmacy_stock = models.ForeignKey(PharmacyStock, on_delete=models.CASCADE, related_name='batches', help_text="Kho thuốc")
    batch_number = models.CharField(max_length=100, help_text="Số lô")
    quantity = models.PositiveIntegerField(help_text="Số lượng trong lô")
    expiry_date = models.DateField(help_text="Ngày hết hạn")
    
    def __str__(self):
        return f"{self.pharmacy_stock.medication.name} - Batch {self.batch_number} - Exp: {self.expiry_date}"

    class Meta:
        verbose_name = "Batch Expiry"
        verbose_name_plural = "Batch Expiries"


class DispenseLog(models.Model):
    """Nhật ký cấp phát thuốc"""
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PENDING_BILLING', 'Pending Billing'),
    ]

    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='dispense_logs', help_text="Đơn thuốc")
    pharmacist_id = models.PositiveIntegerField(help_text="ID dược sĩ từ User Service")
    pharmacist_name = models.CharField(max_length=255, help_text="Tên dược sĩ")
    date_dispensed = models.DateTimeField(default=timezone.now, help_text="Ngày cấp phát")
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='PENDING_BILLING', help_text="Trạng thái thanh toán")
    notes = models.TextField(blank=True, help_text="Ghi chú")
    
    def __str__(self):
        return f"Dispense {self.id} - Prescription {self.prescription.id} - {self.date_dispensed}"

    class Meta:
        verbose_name = "Dispense Log"
        verbose_name_plural = "Dispense Logs"


class DispenseItem(models.Model):
    """Chi tiết cấp phát thuốc"""
    dispense_log = models.ForeignKey(DispenseLog, on_delete=models.CASCADE, related_name='items', help_text="Nhật ký cấp phát")
    prescription_item = models.ForeignKey(PrescriptionItem, on_delete=models.CASCADE, related_name='dispense_items', help_text="Chi tiết đơn thuốc")
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, help_text="Thuốc")
    quantity_dispensed = models.PositiveIntegerField(help_text="Số lượng cấp phát")
    batch_number = models.CharField(max_length=100, blank=True, null=True, help_text="Số lô thuốc cấp phát")
    
    def __str__(self):
        return f"Dispense {self.dispense_log.id} - {self.medication.name} - {self.quantity_dispensed}"

    class Meta:
        verbose_name = "Dispense Item"
        verbose_name_plural = "Dispense Items"
