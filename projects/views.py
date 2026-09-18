from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Project
from clients.models import Client
from accounts.models import User


@login_required
def project_list(request):
    qs = Project.objects.select_related('client', 'project_manager').order_by('-created_at')
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(location__icontains=q))
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'projects/list.html', {
        'page_title': 'Projects', 'projects': page,
        'q': q, 'status': status,
        'status_choices': Project.STATUS_CHOICES,
        'counts': {
            'all': Project.objects.count(),
            'active': Project.objects.filter(status='active').count(),
            'completed': Project.objects.filter(status='completed').count(),
            'upcoming': Project.objects.filter(status='upcoming').count(),
        }
    })


@login_required
def project_add(request):
    clients = Client.objects.filter(is_active=True)
    managers = User.objects.filter(is_active=True).select_related('role')
    if request.method == 'POST':
        try:
            p = Project()
            p.name = request.POST['name']
            p.location = request.POST['location']
            p.project_type = request.POST.get('project_type', 'residential')
            p.start_date = request.POST['start_date']
            p.expected_end_date = request.POST['expected_end_date']
            p.budget = request.POST.get('budget') or 0
            p.status = request.POST.get('status', 'planning')
            p.description = request.POST.get('description', '')
            p.progress = request.POST.get('progress', 0) or 0
            client_id = request.POST.get('client')
            if client_id:
                p.client_id = client_id
            manager_id = request.POST.get('project_manager')
            if manager_id:
                p.project_manager_id = manager_id
            if request.FILES.get('image'):
                p.image = request.FILES['image']
            p.created_by = request.user
            p.save()
            messages.success(request, f'Project "{p.name}" created successfully.')
            return redirect('projects:detail', pk=p.pk)
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
    return render(request, 'projects/form.html', {
        'page_title': 'Add Project', 'clients': clients,
        'managers': managers, 'status_choices': Project.STATUS_CHOICES,
        'type_choices': Project.TYPE_CHOICES,
    })


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project.objects.select_related('client', 'project_manager'), pk=pk)
    from expenses.models import Expense
    from django.db.models import Count
    expenses = project.expenses.order_by('-date')[:10]
    workers = project.employees.filter(status='active')
    daily_reports = project.daily_reports.order_by('-report_date')[:5]
    material_txns = project.material_transactions.select_related('material').order_by('-date')[:10]

    # Cost breakdown
    expense_totals = project.expenses.filter(approval_status='approved').values('category').annotate(
        total=Sum('amount')
    )
    cost_by_cat = {e['category']: float(e['total'] or 0) for e in expense_totals}

    return render(request, 'projects/detail.html', {
        'page_title': project.name, 'project': project,
        'expenses': expenses, 'workers': workers,
        'daily_reports': daily_reports, 'material_txns': material_txns,
        'cost_by_cat': cost_by_cat,
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    clients = Client.objects.filter(is_active=True)
    managers = User.objects.filter(is_active=True).select_related('role')
    if request.method == 'POST':
        try:
            project.name = request.POST['name']
            project.location = request.POST['location']
            project.project_type = request.POST.get('project_type', 'residential')
            project.start_date = request.POST['start_date']
            project.expected_end_date = request.POST['expected_end_date']
            project.budget = request.POST.get('budget') or 0
            project.status = request.POST.get('status', 'planning')
            project.description = request.POST.get('description', '')
            project.progress = request.POST.get('progress', 0) or 0
            client_id = request.POST.get('client')
            project.client_id = client_id if client_id else None
            manager_id = request.POST.get('project_manager')
            project.project_manager_id = manager_id if manager_id else None
            actual_end = request.POST.get('actual_end_date')
            project.actual_end_date = actual_end if actual_end else None
            if request.FILES.get('image'):
                project.image = request.FILES['image']
            project.save()
            messages.success(request, f'Project "{project.name}" updated successfully.')
            return redirect('projects:detail', pk=project.pk)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return render(request, 'projects/form.html', {
        'page_title': 'Edit Project', 'project': project,
        'clients': clients, 'managers': managers,
        'status_choices': Project.STATUS_CHOICES,
        'type_choices': Project.TYPE_CHOICES,
    })


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        name = project.name
        project.delete()
        messages.success(request, f'Project "{name}" deleted.')
    return redirect('projects:list')
