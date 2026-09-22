from django.db import models
from projects.models import Project
from django.conf import settings


class DailyReport(models.Model):
    WEATHER_CHOICES = [
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('windy', 'Windy'),
        ('other', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='daily_reports')
    report_date = models.DateField()
    weather = models.CharField(max_length=10, choices=WEATHER_CHOICES, default='sunny')
    total_workers = models.PositiveIntegerField(default=0)
    present_workers = models.PositiveIntegerField(default=0)
    work_completed = models.TextField(blank=True)
    work_in_progress = models.TextField(blank=True)
    materials_used = models.TextField(blank=True)
    equipment_used = models.TextField(blank=True)
    issues = models.TextField(blank=True)
    safety_incidents = models.TextField(blank=True)
    supervisor_remarks = models.TextField(blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='daily_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_reports'
        ordering = ['-report_date']
        unique_together = ('project', 'report_date')

    def __str__(self):
        return f"{self.project.name} - {self.report_date}"
