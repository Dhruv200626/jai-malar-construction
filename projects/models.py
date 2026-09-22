from django.db import models
from django.conf import settings
from clients.models import Client


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('infrastructure', 'Infrastructure'),
        ('renovation', 'Renovation'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    location = models.CharField(max_length=300)
    project_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='residential')
    start_date = models.DateField()
    expected_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='managed_projects'
    )
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    progress = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='projects/images/', null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def actual_cost(self):
        from expenses.models import Expense
        total = self.expenses.filter(approval_status='approved').aggregate(
            total=models.Sum('amount'))['total'] or 0
        return total

    @property
    def remaining_budget(self):
        return self.budget - self.actual_cost

    @property
    def budget_utilization(self):
        if self.budget > 0:
            return round((self.actual_cost / self.budget) * 100, 1)
        return 0

    def get_status_display_class(self):
        mapping = {
            'planning': 'planning',
            'upcoming': 'upcoming',
            'active': 'active',
            'on_hold': 'on-hold',
            'completed': 'completed',
            'cancelled': 'inactive',
        }
        return mapping.get(self.status, 'secondary')
