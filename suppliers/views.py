from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Supplier


@login_required
def supplier_list(request):
    qs = Supplier.objects.all().order_by('name')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(company__icontains=q) | Q(phone__icontains=q))
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'suppliers/list.html', {'page_title': 'Suppliers', 'suppliers': page, 'q': q})


@login_required
def supplier_add(request):
    if request.method == 'POST':
        try:
            s = Supplier()
            s.name = request.POST['name']
            s.company = request.POST.get('company', '')
            s.phone = request.POST['phone']
            s.email = request.POST.get('email', '')
            s.address = request.POST.get('address', '')
            s.gst_number = request.POST.get('gst_number', '')
            s.materials_supplied = request.POST.get('materials_supplied', '')
            s.notes = request.POST.get('notes', '')
            s.save()
            messages.success(request, f'Supplier "{s.name}" added.')
            return redirect('suppliers:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'suppliers/form.html', {'page_title': 'Add Supplier'})


@login_required
def supplier_edit(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        try:
            s.name = request.POST['name']
            s.company = request.POST.get('company', '')
            s.phone = request.POST['phone']
            s.email = request.POST.get('email', '')
            s.address = request.POST.get('address', '')
            s.gst_number = request.POST.get('gst_number', '')
            s.materials_supplied = request.POST.get('materials_supplied', '')
            s.notes = request.POST.get('notes', '')
            s.save()
            messages.success(request, f'Supplier "{s.name}" updated.')
            return redirect('suppliers:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'suppliers/form.html', {'page_title': 'Edit Supplier', 'supplier': s})


@login_required
def supplier_delete(request, pk):
    s = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        s.delete()
        messages.success(request, 'Supplier deleted.')
    return redirect('suppliers:list')
