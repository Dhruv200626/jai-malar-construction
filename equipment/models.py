from django.db import models
from projects.models import Project


class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ('earthmoving', 'Earth Moving'),
        ('lifting', 'Lifting'),
        ('concrete', 'Concrete'),
        ('transport', 'Transport'),
        ('compaction', 'Compaction'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment')
    owner_vendor = models.CharField(max_length=200, blank=True)
    rental_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rental_per = models.CharField(max_length=20, default='day', blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment'
        ordering = ['name']

    def __str__(self):
        return self.name
