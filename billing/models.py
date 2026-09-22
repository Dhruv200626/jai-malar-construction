"""
Billing — Bill, BillItem models
Relationships: Client → Bill → BillItem
               Supplier → Bill (supplier who provided materials/services)
"""
from django.db import models
from django.conf import settings
from clients.models import Client
from suppliers.models import Supplier
import uuid


def generate_invoice_number():
    """Generate a unique invoice number like INV-2026-0001"""
    from django.utils import timezone
    year = timezone.now().year
    last = Bill.objects.filter(invoice_number__startswith=f'INV-{year}-').order_by('-id').first()
    if last:
        try:
            seq = int(last.invoice_number.split('-')[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f'INV-{year}-{seq:04d}'


class Bill(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
        ('other', 'Other'),
    ]

    invoice_number   = models.CharField(max_length=30, unique=True, blank=True)
    client           = models.ForeignKey(Client,   on_delete=models.PROTECT, related_name='bills')
    supplier         = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='bills')
    bill_date        = models.DateField()
    due_date         = models.DateField(null=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_method   = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')

    # Financials — all computed in view/save, stored for fast retrieval
    subtotal         = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5,  decimal_places=2, default=0)   # e.g. 5.00 = 5%
    discount_amount  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    taxable_amount   = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    gst_percent      = models.DecimalField(max_digits=5,  decimal_places=2, default=18)  # GST %
    cgst_amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    sgst_amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    grand_total      = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    notes            = models.TextField(blank=True)
    terms            = models.TextField(blank=True)

    created_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_bills'
    )
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bills'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} — {self.client}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = generate_invoice_number()
        self.recalculate()
        super().save(*args, **kwargs)

    def recalculate(self):
        """Recompute all financial fields from items."""
        items = self.items.all() if self.pk else []
        self.subtotal = sum(i.amount for i in items)

        discount = self.subtotal * (self.discount_percent / 100)
        self.discount_amount = round(discount, 2)
        self.taxable_amount  = round(self.subtotal - self.discount_amount, 2)

        gst_total = self.taxable_amount * (self.gst_percent / 100)
        self.cgst_amount = round(gst_total / 2, 2)
        self.sgst_amount = round(gst_total / 2, 2)
        self.tax_amount  = round(gst_total, 2)
        self.grand_total = round(self.taxable_amount + self.tax_amount, 2)


class BillItem(models.Model):
    bill        = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=300)
    quantity    = models.DecimalField(max_digits=10, decimal_places=2)
    rate        = models.DecimalField(max_digits=12, decimal_places=2)
    amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    unit        = models.CharField(max_length=30, blank=True)
    hsn_code    = models.CharField(max_length=20, blank=True)  # HSN/SAC code for GST

    class Meta:
        db_table = 'bill_items'

    def __str__(self):
        return f"{self.description} ({self.quantity} × ₹{self.rate})"

    def save(self, *args, **kwargs):
        self.amount = round(self.quantity * self.rate, 2)
        super().save(*args, **kwargs)
