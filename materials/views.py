from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from .models import Material, MaterialTransaction
from suppliers.models import Supplier
from projects.models import Project


@login_required
def material_list(request):
    qs = Material.objects.select_related('supplier').filter(is_active=True)
    q = request.GET.get('q', '')
    cat = request.GET.get('category', '')
    if q:
        qs = qs.filter(Q(name__icontains=q))
    if cat:
        qs = qs.filter(category=cat)
    return render(request, 'materials/list.html', {
        'page_title': 'Materials', 'materials': qs,
        'q': q, 'cat': cat,
        'categories': Material.CATEGORY_CHOICES,
        'low_stock_count': sum(1 for m in qs if m.is_low_stock),
    })


@login_required
def material_add(request):
    suppliers = Supplier.objects.filter(is_active=True)
    if request.method == 'POST':
        try:
            m = Material()
            m.name = request.POST['name']
            m.category = request.POST.get('category', 'other')
            m.unit = request.POST.get('unit', 'pieces')
            m.current_stock = request.POST.get('current_stock') or 0
            m.minimum_stock = request.POST.get('minimum_stock') or 0
            m.unit_price = request.POST.get('unit_price') or 0
            m.description = request.POST.get('description', '')
            sup_id = request.POST.get('supplier')
            m.supplier_id = sup_id if sup_id else None
            m.save()
            messages.success(request, f'Material "{m.name}" added.')
            return redirect('materials:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'materials/form.html', {
        'page_title': 'Add Material',
        'suppliers': suppliers,
        'categories': Material.CATEGORY_CHOICES,
        'units': Material.UNIT_CHOICES,
    })


@login_required
def material_edit(request, pk):
    mat = get_object_or_404(Material, pk=pk)
    suppliers = Supplier.objects.filter(is_active=True)
    if request.method == 'POST':
        try:
            mat.name = request.POST['name']
            mat.category = request.POST.get('category', 'other')
            mat.unit = request.POST.get('unit', 'pieces')
            mat.minimum_stock = request.POST.get('minimum_stock') or 0
            mat.unit_price = request.POST.get('unit_price') or 0
            mat.description = request.POST.get('description', '')
            sup_id = request.POST.get('supplier')
            mat.supplier_id = sup_id if sup_id else None
            mat.save()
            messages.success(request, f'Material "{mat.name}" updated.')
            return redirect('materials:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'materials/form.html', {
        'page_title': 'Edit Material', 'mat': mat,
        'suppliers': suppliers,
        'categories': Material.CATEGORY_CHOICES,
        'units': Material.UNIT_CHOICES,
    })


@login_required
def material_delete(request, pk):
    mat = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        mat.is_active = False
        mat.save()
        messages.success(request, f'Material "{mat.name}" removed.')
    return redirect('materials:list')


@login_required
def inventory(request):
    materials = Material.objects.filter(is_active=True).order_by('name')
    return render(request, 'materials/inventory.html', {
        'page_title': 'Material Inventory', 'materials': materials,
    })


@login_required
def transactions(request):
    qs = MaterialTransaction.objects.select_related('material', 'project', 'supplier').order_by('-date')
    q = request.GET.get('q', '')
    txn_type = request.GET.get('type', '')
    if q:
        qs = qs.filter(material__name__icontains=q)
    if txn_type:
        qs = qs.filter(transaction_type=txn_type)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'materials/transactions.html', {
        'page_title': 'Material Transactions', 'transactions': page,
        'q': q, 'txn_type': txn_type,
        'type_choices': MaterialTransaction.TYPE_CHOICES,
    })


@login_required
def add_transaction(request):
    materials = Material.objects.filter(is_active=True)
    projects = Project.objects.filter(status__in=['active', 'upcoming'])
    suppliers = Supplier.objects.filter(is_active=True)
    if request.method == 'POST':
        try:
            t = MaterialTransaction()
            t.material_id = request.POST['material']
            t.transaction_type = request.POST['transaction_type']
            t.quantity = request.POST['quantity']
            t.unit_price = request.POST.get('unit_price') or 0
            t.date = request.POST['date']
            t.remarks = request.POST.get('remarks', '')
            t.created_by = request.user
            proj_id = request.POST.get('project')
            t.project_id = proj_id if proj_id else None
            sup_id = request.POST.get('supplier')
            t.supplier_id = sup_id if sup_id else None
            t.save()
            messages.success(request, 'Transaction recorded successfully.')
            return redirect('materials:transactions')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'materials/add_transaction.html', {
        'page_title': 'Add Transaction',
        'materials': materials, 'projects': projects, 'suppliers': suppliers,
        'type_choices': MaterialTransaction.TYPE_CHOICES,
    })
