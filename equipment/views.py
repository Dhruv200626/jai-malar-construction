from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Equipment
from projects.models import Project


@login_required
def equipment_list(request):
    qs = Equipment.objects.select_related('project').order_by('name')
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(owner_vendor__icontains=q))
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'equipment/list.html', {
        'page_title': 'Equipment', 'equipment': page,
        'q': q, 'status': status,
        'status_choices': Equipment.STATUS_CHOICES,
    })


@login_required
def equipment_add(request):
    projects = Project.objects.filter(status__in=['active', 'upcoming'])
    if request.method == 'POST':
        try:
            e = Equipment()
            e.name = request.POST['name']
            e.category = request.POST.get('category', 'other')
            e.owner_vendor = request.POST.get('owner_vendor', '')
            e.rental_cost = request.POST.get('rental_cost') or 0
            e.rental_per = request.POST.get('rental_per', 'day')
            e.status = request.POST.get('status', 'available')
            e.notes = request.POST.get('notes', '')
            start = request.POST.get('start_date')
            end = request.POST.get('end_date')
            e.start_date = start if start else None
            e.end_date = end if end else None
            proj_id = request.POST.get('project')
            e.project_id = proj_id if proj_id else None
            e.save()
            messages.success(request, f'Equipment "{e.name}" added.')
            return redirect('equipment:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'equipment/form.html', {
        'page_title': 'Add Equipment', 'projects': projects,
        'categories': Equipment.CATEGORY_CHOICES,
        'status_choices': Equipment.STATUS_CHOICES,
    })


@login_required
def equipment_edit(request, pk):
    eq = get_object_or_404(Equipment, pk=pk)
    projects = Project.objects.filter(status__in=['active', 'upcoming'])
    if request.method == 'POST':
        try:
            eq.name = request.POST['name']
            eq.category = request.POST.get('category', 'other')
            eq.owner_vendor = request.POST.get('owner_vendor', '')
            eq.rental_cost = request.POST.get('rental_cost') or 0
            eq.rental_per = request.POST.get('rental_per', 'day')
            eq.status = request.POST.get('status', 'available')
            eq.notes = request.POST.get('notes', '')
            start = request.POST.get('start_date')
            end = request.POST.get('end_date')
            eq.start_date = start if start else None
            eq.end_date = end if end else None
            proj_id = request.POST.get('project')
            eq.project_id = proj_id if proj_id else None
            eq.save()
            messages.success(request, f'Equipment "{eq.name}" updated.')
            return redirect('equipment:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'equipment/form.html', {
        'page_title': 'Edit Equipment', 'eq': eq, 'projects': projects,
        'categories': Equipment.CATEGORY_CHOICES,
        'status_choices': Equipment.STATUS_CHOICES,
    })


@login_required
def equipment_delete(request, pk):
    eq = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        eq.delete()
        messages.success(request, 'Equipment deleted.')
    return redirect('equipment:list')
