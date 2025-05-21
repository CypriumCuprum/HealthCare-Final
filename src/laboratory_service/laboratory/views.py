from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import TestCatalog, LabOrder, LabOrderItem, LabResult, TestNormalRange
from .serializers import (
    TestCatalogSerializer,
    LabOrderSerializer,
    LabOrderCreateSerializer,
    LabOrderItemSerializer,
    LabResultSerializer,
    LabResultCreateSerializer,
    TestNormalRangeSerializer
)
from .utils import CustomJWTAuthentication, get_user_details


class IsLabTechnicianOrDoctor(permissions.BasePermission):
    """
    Permission để kiểm tra xem người dùng có phải là kỹ thuật viên hoặc bác sĩ không.
    Đây là permission đơn giản để minh họa, thực tế cần tích hợp với User Service.
    """
    def has_permission(self, request, view):
        # Trong thực tế, sẽ lấy thông tin người dùng từ token và kiểm tra vai trò
        # Ở đây chúng ta giả định là mọi người dùng đã xác thực đều được phép
        return request.user is not None


class TestCatalogViewSet(viewsets.ModelViewSet):
    """ViewSet cho danh mục xét nghiệm."""
    queryset = TestCatalog.objects.all()
    serializer_class = TestCatalogSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = TestCatalog.objects.all()
        
        # Filter theo tên hoặc mã
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                test_name__icontains=search) | queryset.filter(
                test_code__icontains=search
            )
        
        return queryset


class LabOrderViewSet(viewsets.ModelViewSet):
    """ViewSet cho phiếu yêu cầu xét nghiệm."""
    queryset = LabOrder.objects.all()
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return LabOrderCreateSerializer
        return LabOrderSerializer

    def get_queryset(self):
        queryset = LabOrder.objects.all()
        
        # Filter theo ID bệnh nhân
        patient_id = self.request.query_params.get('patient_id', None)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter theo ID bác sĩ
        doctor_id = self.request.query_params.get('doctor_id', None)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        # Filter theo trạng thái
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None):
        """Cập nhật trạng thái của phiếu yêu cầu xét nghiệm."""
        lab_order = self.get_object()
        status = request.data.get('status', None)
        
        if not status or status not in dict(LabOrder.STATUS_CHOICES):
            return Response(
                {'status': 'Trạng thái không hợp lệ.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lab_order.status = status
        lab_order.save()
        
        serializer = LabOrderSerializer(lab_order)
        return Response(serializer.data)


class LabOrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet cho chi tiết phiếu yêu cầu xét nghiệm."""
    queryset = LabOrderItem.objects.all()
    serializer_class = LabOrderItemSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None):
        """Cập nhật trạng thái của chi tiết phiếu yêu cầu xét nghiệm."""
        lab_order_item = self.get_object()
        status = request.data.get('status', None)
        
        if not status or status not in dict(LabOrderItem.STATUS_CHOICES):
            return Response(
                {'status': 'Trạng thái không hợp lệ.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lab_order_item.status = status
        lab_order_item.save()
        
        # Cập nhật sample_id nếu được cung cấp
        sample_id = request.data.get('sample_id', None)
        if sample_id:
            lab_order_item.sample_id = sample_id
            lab_order_item.save()
        
        # Nếu status là SAMPLE_COLLECTED, cập nhật status của LabOrder
        if status == 'SAMPLE_COLLECTED':
            lab_order = lab_order_item.lab_order
            all_samples_collected = all(
                item.status in ['SAMPLE_COLLECTED', 'PROCESSING', 'COMPLETED'] 
                for item in lab_order.items.all()
            )
            if all_samples_collected:
                lab_order.status = 'SAMPLE_COLLECTED'
                lab_order.save()
        
        # Nếu status là PROCESSING, cập nhật status của LabOrder
        elif status == 'PROCESSING':
            lab_order = lab_order_item.lab_order
            any_processing = any(
                item.status == 'PROCESSING' 
                for item in lab_order.items.all()
            )
            if any_processing and lab_order.status in ['REQUESTED', 'SAMPLE_COLLECTED']:
                lab_order.status = 'PROCESSING'
                lab_order.save()
        
        serializer = LabOrderItemSerializer(lab_order_item)
        return Response(serializer.data)


class LabResultViewSet(viewsets.ModelViewSet):
    """ViewSet cho kết quả xét nghiệm."""
    queryset = LabResult.objects.all()
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return LabResultCreateSerializer
        return LabResultSerializer

    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Lấy kết quả xét nghiệm theo ID bệnh nhân."""
        patient_id = request.query_params.get('patient_id', None)
        if not patient_id:
            return Response(
                {'error': 'Thiếu patient_id.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lab_results = LabResult.objects.filter(
            lab_order_item__lab_order__patient_id=patient_id
        )
        
        # Lọc theo trạng thái completed
        completed_only = request.query_params.get('completed_only', 'false').lower() == 'true'
        if completed_only:
            lab_results = lab_results.filter(
                lab_order_item__status='COMPLETED'
            )
        
        serializer = LabResultSerializer(lab_results, many=True)
        return Response(serializer.data)


class TestNormalRangeViewSet(viewsets.ModelViewSet):
    """ViewSet cho khoảng tham chiếu xét nghiệm."""
    queryset = TestNormalRange.objects.all()
    serializer_class = TestNormalRangeSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.AllowAny]
