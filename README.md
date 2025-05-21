**Lưu ý chung khi điều chỉnh:**

*   Tất cả các tương tác giữa các service sẽ là các cuộc gọi API trực tiếp (HTTP request/response).
*   Các service sẽ phụ thuộc chặt chẽ hơn vào tính sẵn sàng của nhau.
*   Database per Service: MySQL hoặc MongoDB tùy theo đặc thù của service.
*   API Gateway sẽ là điểm vào duy nhất cho client.
*   Xác thực bằng JWT từ User Service.
*   Cần giải pháp logging tập trung và monitoring.


Directory Struture should be:
/name_service/
├── name_service/
└── name/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    └── views.py  
---

**1. User Service (Dịch vụ Người dùng & Xác thực)**

*   **Mục đích & Phạm vi:** Quản lý thông tin, xác thực và phân quyền cho tất cả người dùng hệ thống (Patient, Doctor, Nurse, Admin, Pharmacist, Insurance Provider, Lab Technician).
*   **Actors tương tác chính:** Tất cả các actors, API Gateway, các services khác (để xác minh token).
*   **Database:** **MySQL**
*   **Thực thể Dữ liệu chính (MySQL Tables - Django Models):**
    *   `User`:
        *   `id` (PrimaryKey, AutoIncrement)
        *   `username` (CharField, unique, max_length=150)
        *   `password` (CharField, hashed, max_length=128)
        *   `email` (EmailField, unique, max_length=254)
        *   `phone_number` (CharField, unique, nullable=True, blank=True, max_length=20)
        *   `first_name` (CharField, max_length=150, blank=True)
        *   `last_name` (CharField, max_length=150, blank=True)
        *   `role_id` (ForeignKey to `Role`, on_delete=models.PROTECT)
        *   `is_active` (BooleanField, default=True)
        *   `is_staff` (BooleanField, default=False)
        *   `date_joined` (DateTimeField, auto_now_add=True)
        *   `profile_picture_url` (URLField, nullable=True, blank=True, max_length=500)
    *   `Role`:
        *   `id` (PrimaryKey, AutoIncrement)
        *   `name` (CharField, unique, max_length=50) (Values: PATIENT, DOCTOR, NURSE, ADMIN, PHARMACIST, INSURANCE_PROVIDER, LAB_TECHNICIAN)
        *   `description` (TextField, blank=True)
    *   `Permission` (Nếu cần phân quyền chi tiết hơn vai trò):
        *   `id` (PrimaryKey, AutoIncrement)
        *   `codename` (CharField, unique, max_length=100) (e.g., `can_create_appointment`)
        *   `name` (CharField, max_length=255)
    *   `RolePermission` (Bảng trung gian cho quan hệ ManyToMany giữa `Role` và `Permission`):
        *   `id` (PrimaryKey, AutoIncrement)
        *   `role_id` (ForeignKey to `Role`)
        *   `permission_id` (ForeignKey to `Permission`)
*   **API Endpoints (DRF):**
    *   `POST /api/v1/users/register/`: Đăng ký người dùng mới.
        *   Payload: `{ "username", "password", "email", "first_name", "last_name", "phone_number", "role_name": "PATIENT" }` (role_name có thể mặc định hoặc chỉ cho phép một số vai trò tự đăng ký)
        *   Response: Thông tin người dùng đã tạo (không bao gồm password).
    *   `POST /api/v1/users/login/`: Đăng nhập.
        *   Payload: `{ "username", "password" }`
        *   Response: `{ "access_token", "refresh_token" }`
    *   `POST /api/v1/users/logout/`: (Tùy chọn, phía client xóa token).
    *   `POST /api/v1/users/token/refresh/`: Làm mới JWT access token.
        *   Payload: `{ "refresh_token" }`
        *   Response: `{ "access_token" }`
    *   `POST /api/v1/users/token/verify/`: (Internal) Xác minh tính hợp lệ của token.
        *   Payload: `{ "token" }`
        *   Response: Thông tin user nếu token hợp lệ, hoặc lỗi.
    *   `GET /api/v1/users/me/`: Lấy thông tin người dùng đang đăng nhập (từ token).
    *   `PUT /api/v1/users/me/`: Cập nhật thông tin người dùng đang đăng nhập.
    *   `POST /api/v1/users/password/change/`: Đổi mật khẩu (yêu cầu mật khẩu cũ).
    *   `POST /api/v1/users/password/reset/`: Yêu cầu reset mật khẩu (gửi email/SMS).
    *   `POST /api/v1/users/password/reset/confirm/`: Xác nhận reset mật khẩu với token.
*   **Tương tác với các Services khác (REST API Calls):**
    *   **API Gateway / Other Services:** Gọi `POST /api/v1/users/token/verify/` để xác thực token trước khi xử lý request.
    *   **Notification Service:**
        *   Sau khi đăng ký thành công: Gọi API `POST /api/v1/notifications/send/` của Notification Service với payload `{ "notification_type": "USER_REGISTERED", "recipient_id": user.id, "channel": "EMAIL", "data": { "user_name": user.username, "confirmation_link": "..." } }`.
        *   Khi yêu cầu reset mật khẩu: Gọi API `POST /api/v1/notifications/send/` của Notification Service với payload `{ "notification_type": "PASSWORD_RESET_REQUESTED", "recipient_id": user.id, "channel": "EMAIL", "data": { "user_name": user.username, "reset_link": "..." } }`.
*   **Công nghệ:** Django, DRF, MySQL, PyJWT (cho JWT).

---

**2. EHR Service (Dịch vụ Hồ sơ Sức khỏe Điện tử)**

*   **Mục đích & Phạm vi:** Quản lý hồ sơ y tế điện tử toàn diện của bệnh nhân, bao gồm lịch sử khám, chẩn đoán, điều trị, và các thông tin y tế liên quan.
*   **Actors tương tác chính:** Patient (view), Doctor (CRUD), Nurse (update vitals).
*   **Database:** **MongoDB**
*   **Thực thể Dữ liệu chính (MongoDB Collections - Ví dụ cấu trúc document):**
    *   `medical_records` (Mỗi document là một hồ sơ bệnh án cho một bệnh nhân):
        ```json
        {
          "_id": "ObjectId(...)",
          "patient_id": 123, // ID từ User Service
          "patient_name": "Nguyen Van A", // Denormalized for convenience
          "blood_type": "O+",
          "allergies": ["Penicillin", "Peanuts"],
          "chronic_conditions": ["Hypertension", "Diabetes Type 2"],
          "medical_history_summary": "...",
          "created_at": "ISODate(...)",
          "updated_at": "ISODate(...)",
          "encounters": [
            {
              "encounter_id": "UUID() or ObjectId()", // Unique ID cho encounter
              "doctor_id": 456,
              "doctor_name": "Dr. Tran Thi B", // Denormalized
              "appointment_id": "appt_xyz123", // ID từ Appointment Service
              "encounter_date": "ISODate(...)",
              "chief_complaint": "Severe headache",
              "history_of_present_illness": "...",
              "physical_examination_findings": "...",
              "diagnoses": [
                { "diagnosis_id": "UUID()", "icd_code": "R51", "description": "Headache", "is_primary": true }
              ],
              "treatment_plans": [
                { "treatment_plan_id": "UUID()", "description": "Rest and Paracetamol", "follow_up_instructions": "Return if not improved in 3 days" }
              ],
              "vital_signs": [
                { "vital_id": "UUID()", "nurse_id": 789, "timestamp": "ISODate(...)", "heart_rate": 80, "blood_pressure": "120/80", "temperature_celsius": 37.0 }
              ],
              "lab_result_references": [ // Tham chiếu đến kết quả xét nghiệm
                { "lab_order_item_id": "lab_item_abc", "test_name": "Complete Blood Count", "result_summary_url": "/api/v1/lab/results/lab_item_abc" }
              ],
              "prescription_references": [ // Tham chiếu đến đơn thuốc
                { "prescription_id": "presc_def", "issue_date": "ISODate(...)", "prescription_details_url": "/api/v1/prescriptions/presc_def" }
              ]
            }
          ]
        }
        ```
*   **API Endpoints (DRF + Djongo/PyMongo):**
    *   `GET /api/v1/ehr/patients/{patient_id}/`: Lấy toàn bộ hồ sơ y tế của bệnh nhân.
    *   `POST /api/v1/ehr/patients/{patient_id}/`: (Ít dùng, thường được tạo ngầm) Tạo hồ sơ y tế cơ bản nếu chưa có.
    *   `GET /api/v1/ehr/patients/{patient_id}/encounters/`: Lấy danh sách các phiên khám.
    *   `POST /api/v1/ehr/patients/{patient_id}/encounters/`: Tạo một phiên khám mới (thêm vào array `encounters`).
        *   Payload: `{ "doctor_id", "appointment_id" (optional), "encounter_date", "chief_complaint", ... }`
    *   `GET /api/v1/ehr/patients/{patient_id}/encounters/{encounter_id}/`: Lấy chi tiết một phiên khám.
    *   `PUT /api/v1/ehr/patients/{patient_id}/encounters/{encounter_id}/`: Cập nhật thông tin phiên khám.
    *   `POST /api/v1/ehr/patients/{patient_id}/encounters/{encounter_id}/diagnoses/`: Thêm chẩn đoán vào phiên khám.
    *   `PUT /api/v1/ehr/patients/{patient_id}/encounters/{encounter_id}/diagnoses/{diagnosis_id}/`: Cập nhật chẩn đoán.
    *   `POST /api/v1/ehr/patients/{patient_id}/encounters/{encounter_id}/vitals/`: Thêm chỉ số sinh tồn.
    *   `POST /api/v1/ehr/internal/patients/{patient_id}/link-appointment/`: (Internal) Được Appointment Service gọi để EHR tạo sườn encounter.
        *   Payload: `{ "appointment_id", "doctor_id", "appointment_time" }`
    *   `POST /api/v1/ehr/internal/patients/{patient_id}/add-prescription-reference/`: (Internal) Được Prescription Service gọi.
        *   Payload: `{ "prescription_id", "issue_date", "medications_summary": "..." }`
    *   `POST /api/v1/ehr/internal/patients/{patient_id}/add-lab-result-reference/`: (Internal) Được Laboratory Service gọi.
        *   Payload: `{ "lab_order_item_id", "test_name", "result_date", "summary_status": "Normal/Abnormal" }`
*   **Tương tác với các Services khác (REST API Calls):**
    *   **User Service:** Gọi API để xác thực token. Có thể gọi API của User Service để lấy thông tin chi tiết của patient/doctor nếu cần (mặc dù ví dụ trên đã denormalize một số thông tin).
    *   *(Service này sẽ NHẬN cuộc gọi từ Appointment, Prescription, Laboratory Services để cập nhật thông tin như mô tả trong API endpoints internal ở trên).*
*   **Công nghệ:** Django, DRF (có thể với Djongo hoặc PyMongo), MongoDB.

---

**3. Appointment Service (Dịch vụ Lịch hẹn)**

*   **Mục đích & Phạm vi:** Quản lý toàn bộ vòng đời của một lịch hẹn, từ việc bệnh nhân đặt lịch, bác sĩ/y tá quản lý lịch, đến việc hủy hoặc hoàn thành lịch hẹn. Quản lý lịch làm việc của bác sĩ.
*   **Actors tương tác chính:** Patient, Doctor, Nurse, Administrator.
*   **Database:** **MySQL**
*   **Thực thể Dữ liệu chính (MySQL Tables - Django Models):**
    *   `Appointment`:
        *   `id` (PrimaryKey, AutoIncrement)
        *   `patient_id` (IntegerField)  // ID từ User Service
        *   `doctor_id` (IntegerField)  // ID từ User Service
        *   `appointment_time` (DateTimeField)
        *   `duration_minutes` (IntegerField, default=30)
        *   `status` (CharField, max_length=20, choices: PENDING, CONFIRMED, CANCELLED_PATIENT, CANCELLED_DOCTOR, COMPLETED, NO_SHOW)
        *   `reason_for_visit` (TextField, blank=True)
        *   `notes_doctor` (TextField, blank=True) // Ghi chú của bác sĩ
        *   `created_at` (DateTimeField, auto_now_add=True)
        *   `updated_at` (DateTimeField, auto_now=True)
    *   `DoctorSchedule` (Lịch làm việc của bác sĩ):
        *   `id` (PrimaryKey, AutoIncrement)
        *   `doctor_id` (IntegerField)
        *   `day_of_week` (IntegerField, choices: 0=Monday...6=Sunday)
        *   `start_time` (TimeField)
        *   `end_time` (TimeField)
        *   `is_available` (BooleanField, default=True) // Có thể dùng để đánh dấu ngày nghỉ đột xuất
        *   `valid_from` (DateField)
        *   `valid_to` (DateField, nullable=True) // Cho lịch có thời hạn
    *   `TimeSlot` (Khe thời gian - có thể được tạo động hoặc lưu trữ nếu cần thiết):
        *   `id` (PrimaryKey, AutoIncrement)
        *   `doctor_id` (IntegerField)
        *   `start_time` (DateTimeField)
        *   `end_time` (DateTimeField)
        *   `is_booked` (BooleanField, default=False)
*   **API Endpoints (DRF):**
    *   **Patient facing:**
        *   `POST /api/v1/appointments/`: Tạo lịch hẹn mới.
            *   Payload: `{ "doctor_id", "appointment_time", "reason_for_visit" }`
        *   `GET /api/v1/patients/{patient_id}/appointments/`: Lấy danh sách lịch hẹn của bệnh nhân (filter by status, date).
        *   `PUT /api/v1/appointments/{appointment_id}/cancel/`: Bệnh nhân hủy lịch hẹn.
    *   **Doctor/Nurse facing:**
        *   `GET /api/v1/doctors/{doctor_id}/appointments/`: Lấy danh sách lịch hẹn của bác sĩ (filter by status, date).
        *   `PUT /api/v1/appointments/{appointment_id}/confirm/`: Bác sĩ xác nhận lịch hẹn.
        *   `PUT /api/v1/appointments/{appointment_id}/complete/`: Bác sĩ đánh dấu hoàn thành lịch hẹn.
        *   `PUT /api/v1/appointments/{appointment_id}/`: Bác sĩ cập nhật thông tin lịch hẹn (e.g., notes_doctor).
    *   **Scheduling/Availability:**
        *   `GET /api/v1/doctors/{doctor_id}/availability/`: Lấy các khe thời gian trống của bác sĩ cho một ngày/tuần.
            *   Params: `date` (YYYY-MM-DD), `days_in_advance`
        *   `(Admin/Doctor) POST /api/v1/doctors/{doctor_id}/schedule/`: Tạo/cập nhật lịch làm việc.
        *   `(Admin/Doctor) GET /api/v1/doctors/{doctor_id}/schedule/`: Xem lịch làm việc.
*   **Tương tác với các Services khác (REST API Calls):**
    *   **User Service:** Gọi `POST /api/v1/users/token/verify/` để xác thực token. Gọi `GET /api/v1/admin/users/{user_id}/` để lấy thông tin chi tiết (tên, email) của Patient, Doctor khi cần (nếu không denormalize).
    *   **Notification Service:**
        *   Sau khi đặt lịch (status PENDING): Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "APPOINTMENT_REQUESTED_PATIENT", ... }` và `{ "notification_type": "APPOINTMENT_REQUESTED_DOCTOR", ... }`.
        *   Sau khi bác sĩ xác nhận (status CONFIRMED): Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "APPOINTMENT_CONFIRMED_PATIENT", ... }`.
        *   Gửi nhắc nhở (dùng Celery Beat trong service này để trigger): Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "APPOINTMENT_REMINDER_PATIENT", ... }` và `{ "notification_type": "APPOINTMENT_REMINDER_DOCTOR", ... }`.
    *   **EHR Service:**
        *   Khi lịch hẹn `COMPLETED`: Gọi API `POST /api/v1/ehr/internal/patients/{patient_id}/link-appointment/` của EHR Service với payload `{ "appointment_id": appointment.id, "doctor_id": appointment.doctor_id, "patient_id": appointment.patient_id, "appointment_time": appointment.appointment_time }`.
    *   **Billing Service:**
        *   Khi lịch hẹn `COMPLETED`: Gọi API `POST /api/v1/billing/internal/create-invoice-for-appointment/` của Billing Service với payload `{ "appointment_id": appointment.id, "patient_id": appointment.patient_id, "doctor_id": appointment.doctor_id, "service_description": "Consultation", "amount": consultation_fee }`.
*   **Công nghệ:** Django, DRF, MySQL, Celery (cho tác vụ nền như gửi nhắc nhở).

---

**4. Prescription & Pharmacy Service (Dịch vụ Đơn thuốc & Nhà thuốc)**

*   **Mục đích & Phạm vi:** Quản lý đơn thuốc từ khi bác sĩ kê đơn đến khi dược sĩ cấp phát, và quản lý kho thuốc của nhà thuốc.
*   **Actors tương tác chính:** Doctor, Patient, Pharmacist, Administrator.
*   **Database:** **MongoDB**
*   **Thực thể Dữ liệu chính (MongoDB Collections - Ví dụ cấu trúc document):**
    *   `medications` (Danh mục thuốc trung tâm):
        ```json
        {
          "_id": "ObjectId(...)",
          "medication_code": "PARA500", // Mã thuốc
          "name": "Paracetamol 500mg",
          "generic_name": "Paracetamol",
          "manufacturer": "ABC Pharma",
          "description": "Pain reliever and fever reducer.",
          "unit_price": 1000.00, // Giá tham khảo
          "dosage_form": "Tablet", // Dạng bào chế
          "strength": "500mg"
        }
        ```
    *   `prescriptions`:
        ```json
        {
          "_id": "ObjectId(...)", // ID đơn thuốc
          "patient_id": 123,
          "patient_name": "Nguyen Van A",
          "doctor_id": 456,
          "doctor_name": "Dr. Tran Thi B",
          "ehr_encounter_id": "encounter_uuid_123", // Optional
          "date_prescribed": "ISODate(...)",
          "status": "PENDING_VERIFICATION", // PENDING_VERIFICATION, VERIFIED, DISPENSED_PARTIAL, DISPENSED_FULL, CANCELLED
          "notes_for_pharmacist": "Take after meals.",
          "items": [
            {
              "item_id": "UUID()",
              "medication_id": "ObjectId(...)", // Ref to medications collection
              "medication_name": "Paracetamol 500mg", // Denormalized
              "dosage": "1 tablet",
              "frequency": "3 times a day",
              "duration_days": 5,
              "instructions": "Take after meals if stomach upset.",
              "quantity_prescribed": 15
            }
          ],
          "dispense_history": [
             { "dispense_log_id": "ObjectId(...)", "pharmacist_id": 101, "date_dispensed": "ISODate(...)", "dispensed_items": [{ "item_id_ref": "UUID()", "quantity_dispensed": 15 }] }
          ]
        }
        ```
    *   `pharmacy_stock` (Quản lý kho của nhà thuốc cụ thể - nếu có nhiều nhà thuốc, cần thêm `pharmacy_id`):
        ```json
        {
          "_id": "ObjectId(...)", // Hoặc medication_id nếu mỗi thuốc chỉ có 1 record tồn kho
          "medication_id": "ObjectId(...)", // Ref to medications collection
          "medication_name": "Paracetamol 500mg",
          "quantity_on_hand": 200,
          "reorder_level": 50,
          "last_stocked_date": "ISODate(...)",
          "expiry_dates": [ // Quản lý theo lô và hạn dùng
            { "batch_number": "B001", "quantity": 100, "expiry_date": "ISODate(...)" }
          ]
        }
        ```
    *   `dispense_logs`: (Có thể nhúng vào `prescriptions` hoặc tách riêng nếu cần truy vấn phức tạp)
        ```json
        {
          "_id": "ObjectId(...)",
          "prescription_id": "ObjectId(...)",
          "pharmacist_id": 101,
          "date_dispensed": "ISODate(...)",
          "dispensed_items": [
            { "prescription_item_id_ref": "UUID()", "medication_id": "ObjectId(...)", "medication_name": "...", "quantity_dispensed": 15 }
          ],
          "payment_status": "PAID" // or PENDING_BILLING
        }
        ```
*   **API Endpoints (DRF + Djongo/PyMongo):**
    *   **(Doctor)**
        *   `POST /api/v1/prescriptions/`: Tạo đơn thuốc mới.
            *   Payload: `{ "patient_id", "doctor_id", "ehr_encounter_id" (opt), "items": [{ "medication_id", "dosage", ... }], "notes_for_pharmacist" }`
    *   **(Patient)**
        *   `GET /api/v1/patients/{patient_id}/prescriptions/`: Xem danh sách đơn thuốc của bệnh nhân.
        *   `GET /api/v1/prescriptions/{prescription_id}/`: Xem chi tiết đơn thuốc.
    *   **(Pharmacist)**
        *   `GET /api/v1/pharmacy/prescriptions/pending/`: Lấy danh sách đơn thuốc cần xác minh/cấp phát.
        *   `PUT /api/v1/pharmacy/prescriptions/{prescription_id}/verify/`: Xác minh đơn thuốc (cập nhật status).
        *   `POST /api/v1/pharmacy/prescriptions/{prescription_id}/dispense/`: Cấp phát thuốc.
            *   Payload: `{ "pharmacist_id", "items_dispensed": [{ "prescription_item_id_ref", "quantity_dispensed" }] }`
            *   Logic: Cập nhật status đơn thuốc, giảm `pharmacy_stock`, tạo `dispense_log`.
        *   `GET /api/v1/pharmacy/stock/`: Lấy thông tin tồn kho.
        *   `PUT /api/v1/pharmacy/stock/{medication_id}/`: Cập nhật tồn kho (nhập thuốc).
    *   **(Admin)**
        *   `GET, POST /api/v1/admin/medications/catalog/`: Quản lý danh mục thuốc trung tâm.
*   **Tương tác với các Services khác (REST API Calls):**
    *   **User Service:** Auth, user info.
    *   **EHR Service:**
        *   Sau khi đơn thuốc được tạo: Gọi API `POST /api/v1/ehr/internal/patients/{patient_id}/add-prescription-reference/` của EHR Service với payload `{ "prescription_id": presc.id, "issue_date": presc.date_prescribed, "patient_id": presc.patient_id, "medications_summary": "..." }`.
    *   **Notification Service:**
        *   Khi đơn thuốc sẵn sàng cho bệnh nhân (sau khi dược sĩ VERIFIED hoặc DISPENSED): Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "PRESCRIPTION_READY_FOR_PICKUP", "recipient_id": patient_id, ... }`.
        *   Khi kho thuốc sắp hết: Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "PHARMACY_STOCK_LOW", "recipient_id": pharmacist_group_or_admin_id, ... }`.
    *   **Billing Service:**
        *   Sau khi thuốc được cấp phát (từ `dispense` API): Gọi API `POST /api/v1/billing/internal/create-invoice-for-medication/` của Billing Service với payload `{ "dispense_log_id": log.id, "patient_id": patient_id, "items": [{ "medication_name", "quantity", "unit_price", "total_price" }] }`.
*   **Công nghệ:** Django, DRF, MongoDB.

---

**5. Billing & Insurance Service (Dịch vụ Thanh toán & Bảo hiểm)**

*   **Mục đích & Phạm vi:** Quản lý hóa đơn viện phí, xử lý thanh toán của bệnh nhân, và quản lý quy trình yêu cầu thanh toán với các công ty bảo hiểm.
*   **Actors tương tác chính:** Patient, Administrator, Insurance Provider.
*   **Database:** **MySQL**
*   **Thực thể Dữ liệu chính (MySQL Tables - Django Models):**
    *   `Invoice`:
        *   `id` (PrimaryKey, AutoIncrement)
        *   `patient_id` (IntegerField)
        *   `invoice_number` (CharField, unique) // Số hóa đơn
        *   `issue_date` (DateField, auto_now_add=True)
        *   `due_date` (DateField)
        *   `sub_total_amount` (DecimalField)
        *   `tax_amount` (DecimalField, default=0)
        *   `discount_amount` (DecimalField, default=0)
        *   `total_amount` (DecimalField) // = sub_total - discount + tax
        *   `amount_paid_by_patient` (DecimalField, default=0)
        *   `amount_paid_by_insurance` (DecimalField, default=0)
        *   `status` (CharField, max_length=20, choices: DRAFT, PENDING_PATIENT, PENDING_INSURANCE, PARTIALLY_PAID, PAID, OVERDUE, CANCELLED, WRITTEN_OFF)
        *   `related_appointment_id` (IntegerField, nullable=True, blank=True)
        *   `related_prescription_dispense_id` (CharField, nullable=True, blank=True) // ID từ Pharmacy
        *   `related_lab_order_id` (CharField, nullable=True, blank=True) // ID từ Laboratory
    *   `InvoiceItem`:
        *   `id` (PrimaryKey, AutoIncrement)
        *   `invoice_id` (ForeignKey to `Invoice`)
        *   `item_type` (CharField, max_length=50, choices: CONSULTATION, MEDICATION, LAB_TEST, OTHER_SERVICE)
        *   `description` (CharField, max_length=255)
        *   `quantity` (DecimalField, default=1)
        *   `unit_price` (DecimalField)
        *   `total_price` (DecimalField) // quantity * unit_price
    *   `Payment`:
        *   `id` (PrimaryKey, AutoIncrement)
        *   `invoice_id` (ForeignKey to `Invoice`, nullable=True) // Có thể thanh toán không qua hóa đơn
        *   `patient_id` (IntegerField)
        *   `payment_date` (DateTimeField, auto_now_add=True)
        *   `amount` (DecimalField)
        *   `payment_method` (CharField, max_length=50, choices: CREDIT_CARD, CASH, BANK_TRANSFER, INSURANCE_PAYOUT, VOUCHER)
        *   `transaction_id` (CharField, max_length=100, nullable=True, blank=True) // Từ cổng thanh toán
        *   `status` (CharField, max_length=20, choices: SUCCESS, FAILED, PENDING, REFUNDED)
        *   `notes` (TextField, blank=True)
    *   `InsurancePolicy`:
        *   `id` (PrimaryKey, AutoIncrement)
        *   `patient_id` (IntegerField)
        *   `insurance_provider_id` (IntegerField, nullable=True) // Nếu Insurance Provider là user
        *   `provider_name` (CharField, max_length=100)
        *   `policy_number` (CharField, max_length=100, unique=True)
        *   `member_id` (CharField, max_length=100)
        *   `valid_from` (DateField)
        *   `valid_to` (DateField)
        *   `coverage_details_json` (JSONField, blank=True) // Lưu chi tiết quyền lợi
        *   `is_active` (BooleanField, default=True)
    *   `InsuranceClaim`:
        *   `id` (PrimaryKey, AutoIncrement)
        *   `invoice_id` (ForeignKey to `Invoice`)
        *   `insurance_policy_id` (ForeignKey to `InsurancePolicy`)
        *   `submission_date` (DateField, auto_now_add=True)
        *   `claim_amount` (DecimalField) // Số tiền yêu cầu bảo hiểm trả
        *   `approved_amount` (DecimalField, nullable=True)
        *   `rejected_amount` (DecimalField, nullable=True)
        *   `status` (CharField, max_length=30, choices: SUBMITTED, PROCESSING, AWAITING_DOCUMENTS, APPROVED, PARTIALLY_APPROVED, REJECTED, PAID_BY_INSURER, CLOSED)
        *   `insurer_notes` (TextField, blank=True)
        *   `hospital_notes` (TextField, blank=True)
*   **API Endpoints (DRF):**
    *   **(Internal - Được các service khác gọi để tạo hóa đơn)**
        *   `POST /api/v1/billing/internal/create-invoice-for-appointment/`:
            *   Payload: `{ "appointment_id", "patient_id", "doctor_id", "service_description", "amount" }`
        *   `POST /api/v1/billing/internal/create-invoice-for-medication/`:
            *   Payload: `{ "dispense_log_id", "patient_id", "items": [{ "medication_name", "quantity", "unit_price", "total_price" }] }`
        *   `POST /api/v1/billing/internal/create-invoice-for-labtest/`:
            *   Payload: `{ "lab_order_id", "patient_id", "items": [{ "test_name", "price" }] }`
    *   **(Patient facing)**
        *   `GET /api/v1/patients/{patient_id}/invoices/`: Lấy danh sách hóa đơn.
        *   `GET /api/v1/invoices/{invoice_id}/`: Xem chi tiết hóa đơn.
        *   `POST /api/v1/invoices/{invoice_id}/pay/`: Bệnh nhân thanh toán hóa đơn (tích hợp cổng thanh toán).
            *   Payload: `{ "payment_method", "amount", "card_details_if_applicable" }`
        *   `GET, POST /api/v1/patients/{patient_id}/insurance-policies/`: Quản lý thông tin bảo hiểm.
    *   **(Administrator facing)**
        *   `GET /api/v1/admin/invoices/`: Xem tất cả hóa đơn (có filter, sort).
        *   `POST /api/v1/admin/invoices/`: Tạo hóa đơn thủ công.
        *   `PUT /api/v1/admin/invoices/{invoice_id}/`: Cập nhật hóa đơn (e.g., thêm discount, ghi nhận thanh toán tay).
        *   `POST /api/v1/invoices/{invoice_id}/claims/`: Tạo yêu cầu bảo hiểm cho hóa đơn.
        *   `GET /api/v1/admin/claims/`: Xem danh sách yêu cầu bảo hiểm.
        *   `PUT /api/v1/admin/claims/{claim_id}/`: Cập nhật trạng thái yêu cầu bảo hiểm.
    *   **(Insurance Provider - nếu có API trực tiếp)**
        *   `GET /api/v1/insurance-provider/claims/pending/`: Xem các claim đang chờ xử lý từ nhà cung cấp.
        *   `PUT /api/v1/insurance-provider/claims/{claim_id}/process/`: Xử lý claim (approve/reject, ghi nhận số tiền).
*   **Tương tác với các Services khác (REST API Calls):**
    *   *(Service này NHẬN cuộc gọi từ Appointment, Pharmacy, Laboratory Services để tạo invoice items như mô tả trong API internal ở trên).*
    *   **User Service:** Auth, user info.
    *   **Notification Service:**
        *   Khi hóa đơn được tạo: Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "INVOICE_GENERATED", "recipient_id": patient_id, "data": {"invoice_number", "amount", "due_date"} }`.
        *   Khi thanh toán thành công: Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "PAYMENT_SUCCESSFUL", ... }`.
        *   Khi trạng thái claim thay đổi: Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "INSURANCE_CLAIM_STATUS_UPDATED", ... }`.
    *   **External Payment Gateway (e.g., Stripe, PayPal):** Tích hợp để xử lý thanh toán online.
    *   **External Insurance Provider System:** (Nếu có) Tích hợp API để gửi/nhận thông tin claim tự động.
*   **Công nghệ:** Django, DRF, MySQL, tích hợp với cổng thanh toán.

---

**6. Laboratory Service (Dịch vụ Xét nghiệm)**

*   **Mục đích & Phạm vi:** Quản lý toàn bộ quy trình xét nghiệm từ khi bác sĩ yêu cầu, thu thập mẫu, thực hiện xét nghiệm, đến khi trả kết quả cho bác sĩ và bệnh nhân.
*   **Actors tương tác chính:** Doctor, Laboratory Technician, Patient, Administrator.
*   **Database:** **MongoDB**
*   **Thực thể Dữ liệu chính (MongoDB Collections - Ví dụ cấu trúc document):**
    *   `lab_test_catalog` (Danh mục các loại xét nghiệm):
        ```json
        {
          "_id": "ObjectId(...)",
          "test_code": "CBC", // Mã xét nghiệm
          "test_name": "Complete Blood Count",
          "description": "Measures various components of blood.",
          "sample_type_required": "Whole Blood (EDTA)",
          "turn_around_time_hours": 2,
          "price": 150000.00,
          "normal_ranges_template": { // Có thể lưu template dải tham chiếu
             "hemoglobin": {"unit": "g/dL", "male_min": 13.5, "male_max": 17.5, "female_min": 12.0, "female_max": 15.5 }
          }
        }
        ```
    *   `lab_orders` (Yêu cầu xét nghiệm):
        ```json
        {
          "_id": "ObjectId(...)", // ID của order
          "patient_id": 123,
          "patient_name": "Nguyen Van A",
          "doctor_id": 456,
          "doctor_name": "Dr. Tran Thi B",
          "ehr_encounter_id": "encounter_uuid_123", // Optional
          "order_date": "ISODate(...)",
          "status": "SAMPLE_COLLECTED", // REQUESTED, SAMPLE_COLLECTED, PROCESSING, RESULTS_PENDING_REVIEW, COMPLETED, CANCELLED
          "priority": "ROUTINE", // ROUTINE, URGENT
          "notes_for_lab": "Patient is fasting.",
          "items": [ // Các xét nghiệm trong order
            {
              "item_id": "UUID()", // Unique ID cho từng test trong order
              "test_catalog_id": "ObjectId(...)", // Ref to lab_test_catalog
              "test_code": "CBC",
              "test_name": "Complete Blood Count",
              "sample_id": "SAMP00123", // Nếu quản lý mẫu riêng
              "item_status": "PROCESSING", // Trạng thái riêng của từng test
              "result": { // Kết quả sẽ được điền vào đây
                "technician_id": 201,
                "result_date": "ISODate(...)",
                "verified_by_id": 202, // Nếu có quy trình xác minh
                "result_values": {
                  "hemoglobin": 14.0, "unit": "g/dL", "is_abnormal": false,
                  "hematocrit": 42.0, "unit": "%", "is_abnormal": false
                },
                "interpretation": "Within normal limits.",
                "result_file_url": "s3://bucket/results/cbc_result.pdf" // Optional
              }
            }
          ]
        }
        ```
*   **API Endpoints (DRF + Djongo/PyMongo):**
    *   **(Doctor)**
        *   `POST /api/v1/lab/orders/`: Tạo yêu cầu xét nghiệm mới.
            *   Payload: `{ "patient_id", "doctor_id", "items": [{"test_catalog_id", "priority"}], "notes_for_lab" }`
        *   `GET /api/v1/patients/{patient_id}/lab-results/`: Xem danh sách kết quả xét nghiệm của bệnh nhân (chỉ các order đã COMPLETED).
        *   `GET /api/v1/lab/orders/{order_id}/results/`: Xem chi tiết kết quả của một order.
    *   **(Patient)**
        *   `GET /api/v1/patients/{patient_id}/lab-results/`: Xem kết quả xét nghiệm của mình (có thể có độ trễ hoặc cần bác sĩ release).
    *   **(Laboratory Technician)**
        *   `GET /api/v1/lab/orders/pending/`: Lấy danh sách order cần xử lý (REQUESTED, SAMPLE_COLLECTED).
        *   `PUT /api/v1/lab/orders/{order_id}/status/`: Cập nhật trạng thái chung của order (e.g., SAMPLE_COLLECTED).
        *   `PUT /api/v1/lab/orders/{order_id}/items/{item_id}/status/`: Cập nhật trạng thái của một test item (e.g., PROCESSING).
        *   `POST /api/v1/lab/orders/{order_id}/items/{item_id}/results/`: Nhập/Tải lên kết quả cho một test item.
            *   Payload: `{ "technician_id", "result_values": {...}, "interpretation", "result_file_url" }`
    *   **(Administrator)**
        *   `GET, POST /api/v1/admin/lab-tests/catalog/`: Quản lý danh mục xét nghiệm.
        *   `GET, PUT, DELETE /api/v1/admin/lab-tests/catalog/{test_id}/`: Quản lý xét nghiệm cụ thể.
*   **Tương tác với các Services khác (REST API Calls):**
    *   **User Service:** Auth, user info.
    *   **EHR Service:**
        *   Khi kết quả của một `lab_order_item` sẵn sàng và đã được review/complete: Gọi API `POST /api/v1/ehr/internal/patients/{patient_id}/add-lab-result-reference/` của EHR Service với payload `{ "lab_order_item_id": item.item_id, "patient_id": order.patient_id, "test_name": item.test_name, "result_date": item.result.result_date, "summary_status": "Normal/Abnormal based on item.result.is_abnormal" }`.
    *   **Notification Service:**
        *   Khi kết quả xét nghiệm hoàn chỉnh và sẵn sàng cho bác sĩ: Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "LAB_RESULT_READY_DOCTOR", "recipient_id": doctor_id, "data": {"patient_name", "order_id"} }`.
        *   Khi kết quả sẵn sàng cho bệnh nhân (có thể sau khi bác sĩ review): Gọi `POST /api/v1/notifications/send/` với `{ "notification_type": "LAB_RESULT_READY_PATIENT", "recipient_id": patient_id, ... }`.
    *   **Billing Service:**
        *   Khi một `lab_order` được đánh dấu là các xét nghiệm đã thực hiện (có thể là khi `SAMPLE_COLLECTED` hoặc một trạng thái tương tự, tùy quy trình): Gọi API `POST /api/v1/billing/internal/create-invoice-for-labtest/` của Billing Service với payload `{ "lab_order_id": order.id, "patient_id": order.patient_id, "items": [{ "test_name": item.test_name, "price": catalog_item.price }] }`.
*   **Công nghệ:** Django, DRF, MongoDB, S3 hoặc MinIO (để lưu file kết quả PDF).

---

**7. Notification Service (Dịch vụ Thông báo)**

*   **Mục đích & Phạm vi:** Gửi các thông báo (Email, SMS, Push Notification) đến người dùng dựa trên các yêu cầu từ các service khác trong hệ thống.
*   **Actors tương tác chính:** (Gián tiếp) Tất cả người dùng. (Trực tiếp) Các services khác trong hệ thống.
*   **Database:** **MongoDB** (Linh hoạt cho việc lưu trữ templates và logs)
*   **Thực thể Dữ liệu chính (MongoDB Collections - Ví dụ cấu trúc document):**
    *   `notification_templates`:
        ```json
        {
          "_id": "ObjectId(...)",
          "notification_type": "APPOINTMENT_CONFIRMED_PATIENT", // Mã định danh duy nhất cho loại thông báo
          "channel": "EMAIL", // EMAIL, SMS, PUSH
          "language": "vi", // Hỗ trợ đa ngôn ngữ
          "subject_template": "Lịch hẹn của bạn đã được xác nhận: {{appointment_time}}", // Sử dụng template engine (e.g., Jinja2)
          "body_template_html": "<p>Xin chào {{patient_name}},</p><p>Lịch hẹn của bạn với bác sĩ {{doctor_name}} vào lúc {{appointment_time}} đã được xác nhận.</p>",
          "body_template_text": "Xin chào {{patient_name}}, Lịch hẹn của bạn với bác sĩ {{doctor_name}} vào lúc {{appointment_time}} đã được xác nhận.", // Cho SMS hoặc email text
          "is_active": true
        }
        ```
    *   `notification_logs`:
        ```json
        {
          "_id": "ObjectId(...)",
          "recipient_id": 123, // ID người dùng từ User Service
          "recipient_contact": "patient@example.com", // Email/Phone/Push Token đã gửi tới
          "notification_type": "APPOINTMENT_CONFIRMED_PATIENT",
          "channel": "EMAIL",
          "status": "SENT", // PENDING, SENT, FAILED, DELIVERED (nếu có webhook từ provider)
          "sent_at": "ISODate(...)",
          "provider_message_id": "sendgrid_msg_id_xyz", // ID từ dịch vụ gửi
          "error_message": null, // Nếu status là FAILED
          "rendered_subject": "Lịch hẹn của bạn đã được xác nhận: 2023-12-25 10:00", // Nội dung đã render (tùy chọn, để debug)
          "rendered_body": "...",
          "payload_data_received": { "patient_name": "...", ... } // Dữ liệu nhận được để render (tùy chọn)
        }
        ```
*   **API Endpoints (DRF + Djongo/PyMongo):**
    *   **Endpoint chính được các service khác gọi:**
        *   `POST /api/v1/notifications/send/`:
            *   Payload:
                ```json
                {
                  "notification_type": "APPOINTMENT_CONFIRMED_PATIENT",
                  "recipient_id": 123, // Bắt buộc
                  "channel_preferences": ["EMAIL", "SMS"], // Tùy chọn, nếu không có thì service tự quyết định hoặc theo cấu hình user
                  "data": { // Dữ liệu để điền vào template
                    "patient_name": "Nguyen Van A",
                    "doctor_name": "Dr. Tran Thi B",
                    "appointment_time": "2023-12-25 10:00"
                  }
                }
                ```
            *   Logic:
                1.  Xác thực request (có thể yêu cầu token riêng cho service-to-service).
                2.  Lấy thông tin liên hệ của `recipient_id` từ User Service (email, phone).
                3.  Dựa vào `notification_type` và `channel_preferences` (hoặc default), tìm `NotificationTemplate` phù hợp.
                4.  Render template với `data`.
                5.  Gửi thông báo qua kênh tương ứng (tích hợp Email/SMS/Push provider). (Nên dùng Celery task ở đây để không block request).
                6.  Tạo `NotificationLog`.
            *   Response: `{ "status": "QUEUED" }` hoặc `{ "status": "SENT", "log_id": "..." }` (nếu gửi đồng bộ cho trường hợp khẩn cấp).
    *   **(Admin)**
        *   `GET, POST /api/v1/admin/notification-templates/`: Quản lý mẫu thông báo.
        *   `GET, PUT, DELETE /api/v1/admin/notification-templates/{template_id}/`: Quản lý mẫu cụ thể.
        *   `GET /api/v1/admin/notification-logs/`: Xem log gửi thông báo (có filter).
*   **Tương tác với các Services khác (REST API Calls):**
    *   *(Service này NHẬN cuộc gọi API từ tất cả các service khác khi chúng cần gửi thông báo, thông qua endpoint `/api/v1/notifications/send/`)*.
    *   **User Service:**
        *   Gọi `GET /api/v1/admin/users/{user_id}/contact-info/` (hoặc một endpoint tương tự) của User Service để lấy email, số điện thoại, push token của `recipient_id` nếu thông tin này không được gửi kèm trong payload của `/send/` API.
    *   **External Gateways/Providers:**
        *   Email: SendGrid, Amazon SES, Mailgun (qua API của họ).
        *   SMS: Twilio, Vonage, Infobip (qua API của họ).
        *   Push Notifications: Firebase Cloud Messaging (FCM), Apple Push Notification service (APNS).
*   **Công nghệ:** Django, DRF, MongoDB, Celery (cho việc gửi bất đồng bộ), tích hợp với các dịch vụ gửi Email/SMS/Push.

---

**8. Admin Service (Dịch vụ Quản trị Hệ thống - Tùy chọn)**

*   **Mục đích & Phạm vi:** Cung cấp một giao diện quản trị tập trung cho các chức năng quản lý hệ thống tổng thể, tổng hợp dữ liệu hoặc thực hiện các tác vụ không thuộc về một service nghiệp vụ cụ thể nào.
*   **Lưu ý:** Nhiều chức năng quản trị đã được tích hợp vào các service liên quan. Service này chỉ nên tồn tại nếu có nhu cầu quản trị thực sự riêng biệt và phức tạp.
*   **Database:** Có thể là **MySQL** hoặc **MongoDB**, tùy thuộc vào loại dữ liệu quản trị cần lưu trữ (nếu có). Thường thì service này sẽ không có nhiều dữ liệu riêng mà chủ yếu là tổng hợp từ các service khác.
*   **Ví dụ Thực thể Dữ liệu chính (Nếu có):**
    *   `SystemConfiguration` (MySQL/MongoDB):
        *   `key` (CharField/String, unique)
        *   `value` (JSONField/Object)
        *   `description` (TextField/String)
    *   `AuditLog` (MongoDB - nếu không dùng giải pháp logging tập trung riêng):
        *   `timestamp`, `user_id`, `service_name`, `action_performed`, `details`
*   **API Endpoints (DRF):**
    *   `GET /api/v1/admin/dashboard/summary/`: Lấy dữ liệu tổng hợp cho dashboard (gọi API của các service khác).
    *   `GET, PUT /api/v1/admin/system-configurations/{key}/`: Quản lý cấu hình hệ thống.
    *   `GET /api/v1/admin/audit-logs/`: Xem log hành động quản trị.
    *   Các API để trigger các tác vụ quản trị batch (ví dụ: `POST /api/v1/admin/tasks/recalculate-reports/`).
*   **Tương tác với các Services khác (REST API Calls):**
    *   Service này sẽ **GỌI API** của nhiều service khác để:
        *   Lấy dữ liệu (ví dụ: số lượng người dùng từ User Service, số lịch hẹn từ Appointment Service).
        *   Thực hiện các hành động quản trị (ví dụ: vô hiệu hóa người dùng qua User Service).
    *   **User Service:** Xác thực quản trị viên.
*   **Công nghệ:** Django, DRF, cơ sở dữ liệu tùy chọn.

---