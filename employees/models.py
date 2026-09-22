from django.db import models
from projects.models import Project


class Employee(models.Model):
    TYPE_CHOICES = [
        ('engineer', 'Engineer'),
        ('architect', 'Architect'),
        ('supervisor', 'Supervisor'),
        ('mason', 'Mason'),
        ('carpenter', 'Carpenter'),
        ('electrician', 'Electrician'),
        ('plumber', 'Plumber'),
        ('labour', 'Labour / Worker'),
        ('driver', 'Driver'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]
    DEPT_CHOICES = [
        ('civil', 'Civil'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('management', 'Management'),
        ('labour', 'Labour'),
        ('other', 'Other'),
    ]

    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    joining_date = models.DateField()
    designation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=30, choices=DEPT_CHOICES, default='labour')
    employee_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='labour')
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    assigned_project = models.ForeignKey(
        Project, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='employees'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    profile_photo = models.ImageField(upload_to='employees/photos/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last = Employee.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.employee_id = f"EMP{next_id:04d}"
        super().save(*args, **kwargs)

    @property
    def initials(self):
        parts = self.full_name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return self.full_name[:2].upper()
