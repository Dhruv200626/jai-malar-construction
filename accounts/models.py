"""
Accounts - User model with Role-based access control
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """User roles for role-based access control"""
    ADMIN = 'admin'
    PROJECT_MANAGER = 'project_manager'
    SITE_SUPERVISOR = 'site_supervisor'
    EMPLOYEE = 'employee'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (PROJECT_MANAGER, 'Project Manager'),
        (SITE_SUPERVISOR, 'Site Supervisor'),
        (EMPLOYEE, 'Employee'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=15, blank=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    profile_photo = models.ImageField(
        upload_to='users/photos/',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def role_name(self):
        if self.role:
            return self.role.name
        return None

    def is_admin(self):
        return self.role and self.role.name == Role.ADMIN

    def is_project_manager(self):
        return self.role and self.role.name == Role.PROJECT_MANAGER

    def is_site_supervisor(self):
        return self.role and self.role.name == Role.SITE_SUPERVISOR

    def is_employee_role(self):
        return self.role and self.role.name == Role.EMPLOYEE
