from django.contrib import admin
from .models import Bill, BillItem


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'supplier', 'bill_date', 'grand_total', 'status']
    list_filter = ['status', 'bill_date']
    search_fields = ['invoice_number', 'client__name']
    inlines = [BillItemInline]


@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ['bill', 'description', 'quantity', 'rate', 'amount']
