from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    PermissionViewSet,
    RegisterView,
    RolePermissionViewSet,
    RoleViewSet,
    TokenRefreshView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'role-permissions', RolePermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 