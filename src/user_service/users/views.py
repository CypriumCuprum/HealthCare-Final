from django.shortcuts import render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from django.shortcuts import get_object_or_404

from .models import User, Role, Permission, RolePermission
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    PermissionSerializer,
    RolePermissionSerializer,
    RoleSerializer,
    TokenRefreshSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .utils import CustomJWTAuthentication


class LoginView(generics.GenericAPIView):
    """View for user login."""
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': refresh,
            'access': access
        })


class TokenRefreshView(TokenRefreshView):
    """View for refreshing an access token."""
    serializer_class = TokenRefreshSerializer


class TokenVerifyView(generics.GenericAPIView):
    """View for verifying a token."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        token = request.data.get('token', '')
        
        try:
            # Sử dụng CustomJWTAuthentication
            jwt_auth = CustomJWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            
            # Trích xuất thông tin từ token
            user_id = validated_token.get('user_id')
            role = validated_token.get('role')
            
            if user_id:
                # Token hợp lệ, trả về user_id và role
                return Response({
                    'valid': True,
                    'user_id': user_id,
                    'role': {'name': role} if role else None
                }, status=status.HTTP_200_OK)
                
            return Response({'valid': False}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Token verification failed: {str(e)}")
            return Response({'valid': False}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    """View for registering a new user."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update the current user's information."""
        user = request.user
        
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = UserUpdateSerializer(
                user,
                data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password."""
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': ['Wrong password.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing roles."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class PermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing permissions."""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class RolePermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing role permissions."""
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
