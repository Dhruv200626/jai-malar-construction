from django.db import models
from suppliers.models import Supplier
from projects.models import Project
from django.conf import settings


class Material(models.Model):
    CATEGORY_CHOICES = [
        ('cement', 'Cement'),
        ('steel', 'Steel'),
        ('sand', 'Sand'),
        ('bricks', 'Bricks'),
        ('paint', 'Paint'),
        ('tiles', 'Tiles'),
        ('aggregate', 'Aggregate'),
        ('electrical', 'Electrical Material'),
        ('plumbing', 'Plumbing Material'),
        ('wood', 'Wood / Timber'),
        ('glass', 'Glass'),
        ('other', 'Other'),
    ]
    UNIT_CHOICES = [
        ('bags', 'Bags'),
        ('kg', 'Kg'),
        ('ton', 'Ton'),
        ('pieces', 'Pieces'),
        ('meter', 'Meter'),
        ('sqft', 'Sqft'),
        ('litre', 'Litre'),
        ('cubic_meter', 'Cubic Meter'),
        ('nos', 'Nos'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pieces')
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='materials')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'materials'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"

    @property
    def stock_value(self):
        return self.current_stock * self.unit_price

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock and self.minimum_stock > 0

    @property
    def usage_percent(self):
        total_purchased = self.transactions.filter(
            transaction_type='purchase'
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        if total_purchased > 0:
            used = total_purchased - float(self.current_stock)
            return min(round((used / float(total_purchased)) * 100, 1), 100)
        return 0


class MaterialTransaction(models.Model):
    TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('usage', 'Usage'),
        ('return', 'Return'),
        ('damage', 'Damage'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
    ]

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='material_transactions')
    transaction_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    remarks = models.CharField(max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='material_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'material_transactions'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.material.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        # Calculate total
        if self.unit_price and self.quantity:
            self.total_amount = self.unit_price * self.quantity

        # Adjust stock
        if self.pk is None:  # New transaction only
            mat = self.material
            qty = float(self.quantity)
            t = self.transaction_type
            if t == 'purchase' or t == 'return' or t == 'adjustment':
                mat.current_stock += qty
            elif t == 'usage' or t == 'damage' or t == 'transfer':
                mat.current_stock = max(0, float(mat.current_stock) - qty)
            mat.save(update_fields=['current_stock'])

        super().save(*args, **kwargs)
