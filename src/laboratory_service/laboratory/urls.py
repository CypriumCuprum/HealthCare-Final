from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TestCatalogViewSet,
    LabOrderViewSet,
    LabOrderItemViewSet,
    LabResultViewSet,
    TestNormalRangeViewSet
)

router = DefaultRouter()
router.register(r'tests', TestCatalogViewSet)
router.register(r'lab-orders', LabOrderViewSet)
router.register(r'lab-order-items', LabOrderItemViewSet)
router.register(r'lab-results', LabResultViewSet)
router.register(r'test-normal-ranges', TestNormalRangeViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 