from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Role(models.Model):
    """Model for user roles in the system."""
    PATIENT = 'PATIENT'
    DOCTOR = 'DOCTOR'
    NURSE = 'NURSE'
    ADMIN = 'ADMIN'
    PHARMACIST = 'PHARMACIST'
    INSURANCE_PROVIDER = 'INSURANCE_PROVIDER'
    LAB_TECHNICIAN = 'LAB_TECHNICIAN'

    ROLE_CHOICES = [
        (PATIENT, 'Patient'),
        (DOCTOR, 'Doctor'),
        (NURSE, 'Nurse'),
        (ADMIN, 'Admin'),
        (PHARMACIST, 'Pharmacist'),
        (INSURANCE_PROVIDER, 'Insurance Provider'),
        (LAB_TECHNICIAN, 'Lab Technician'),
    ]

    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        verbose_name='Role name'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        for role_code, role_name in self.ROLE_CHOICES:
            if role_code == self.name:
                return role_name
        return self.name


class Permission(models.Model):
    """Model for granular permissions in the system."""
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Permission codename'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Permission name'
    )

    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Model for mapping permissions to roles."""
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions',
        verbose_name='Role'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions',
        verbose_name='Permission'
    )

    class Meta:
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role} - {self.permission}"


class User(models.Model):
    """Custom user model for the healthcare system."""
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        unique=True,
    )
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
    )
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_picture_url = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def get_full_name(self):
        """Return the user's full name."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.username

    def set_password(self, raw_password):
        """Set the user's password."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the given password is correct."""
        return check_password(raw_password, self.password)

    def has_permission(self, permission_codename):
        """Check if user has a specific permission through their role."""
        try:
            return self.role.role_permissions.filter(
                permission__codename=permission_codename
            ).exists()
        except RolePermission.DoesNotExist:
            return False

    @property
    def is_authenticated(self):
        """
        Always return True for authenticated users.
        Required by Django's auth system.
        """
        return True
        
    @property
    def is_anonymous(self):
        """
        Always return False for authenticated users.
        Required by Django's auth system.
        """
        return False
