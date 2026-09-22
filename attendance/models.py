from django.db import models
from employees.models import Employee
from projects.models import Project
from django.utils import timezone


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('leave', 'Leave'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendances')
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    working_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    remarks = models.CharField(max_length=300, blank=True)
    marked_by = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.status}"

    def save(self, *args, **kwargs):
        # Auto calculate working hours
        if self.check_in and self.check_out:
            from datetime import datetime, date
            dt_in = datetime.combine(date.today(), self.check_in)
            dt_out = datetime.combine(date.today(), self.check_out)
            diff = (dt_out - dt_in).total_seconds() / 3600
            if diff > 0:
                standard = 8.0
                self.working_hours = round(min(diff, 24), 2)
                if diff > standard:
                    self.overtime_hours = round(diff - standard, 2)
        super().save(*args, **kwargs)
