from django.db import models
from projects.models import Project
from django.conf import settings


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('labour', 'Labour'),
        ('material', 'Material'),
        ('equipment', 'Equipment'),
        ('transport', 'Transport'),
        ('salary', 'Salary'),
        ('electricity', 'Electricity'),
        ('water', 'Water'),
        ('contractor', 'Contractor'),
        ('other', 'Other'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
        ('other', 'Other'),
    ]
    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    vendor = models.CharField(max_length=200, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    receipt = models.FileField(upload_to='expenses/receipts/', null=True, blank=True)
    description = models.TextField(blank=True)
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_expenses'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_expenses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expenses'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_category_display()} - ₹{self.amount} ({self.date})"
