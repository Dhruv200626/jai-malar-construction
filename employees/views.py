from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Employee
from projects.models import Project


@login_required
def employee_list(request):
    qs = Employee.objects.select_related('assigned_project').order_by('full_name')
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    emp_type = request.GET.get('type', '')
    project_id = request.GET.get('project', '')
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(employee_id__icontains=q))
    if status:
        qs = qs.filter(status=status)
    if emp_type:
        qs = qs.filter(employee_type=emp_type)
    if project_id:
        qs = qs.filter(assigned_project_id=project_id)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'employees/list.html', {
        'page_title': 'Workers & Employees', 'employees': page,
        'q': q, 'status': status, 'emp_type': emp_type,
        'projects': Project.objects.filter(status='active'),
        'type_choices': Employee.TYPE_CHOICES,
        'status_choices': Employee.STATUS_CHOICES,
        'total': Employee.objects.count(),
        'active': Employee.objects.filter(status='active').count(),
    })


@login_required
def employee_add(request):
    projects = Project.objects.filter(status__in=['active', 'upcoming'])
    if request.method == 'POST':
        try:
            e = Employee()
            e.full_name = request.POST['full_name']
            e.phone = request.POST['phone']
            e.email = request.POST.get('email', '')
            e.address = request.POST.get('address', '')
            e.joining_date = request.POST['joining_date']
            e.designation = request.POST.get('designation', '')
            e.department = request.POST.get('department', 'labour')
            e.employee_type = request.POST.get('employee_type', 'labour')
            e.salary = request.POST.get('salary') or 0
            e.status = request.POST.get('status', 'active')
            e.notes = request.POST.get('notes', '')
            dob = request.POST.get('date_of_birth')
            e.date_of_birth = dob if dob else None
            proj_id = request.POST.get('assigned_project')
            e.assigned_project_id = proj_id if proj_id else None
            if request.FILES.get('profile_photo'):
                e.profile_photo = request.FILES['profile_photo']
            e.save()
            messages.success(request, f'Worker "{e.full_name}" added successfully.')
            return redirect('employees:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'employees/form.html', {
        'page_title': 'Add Worker', 'projects': projects,
        'type_choices': Employee.TYPE_CHOICES,
        'status_choices': Employee.STATUS_CHOICES,
        'dept_choices': Employee.DEPT_CHOICES,
    })


@login_required
def employee_detail(request, pk):
    emp = get_object_or_404(Employee.objects.select_related('assigned_project'), pk=pk)
    attendances = emp.attendances.order_by('-date')[:30]
    return render(request, 'employees/detail.html', {
        'page_title': emp.full_name, 'emp': emp, 'attendances': attendances,
    })


@login_required
def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    projects = Project.objects.filter(status__in=['active', 'upcoming'])
    if request.method == 'POST':
        try:
            emp.full_name = request.POST['full_name']
            emp.phone = request.POST['phone']
            emp.email = request.POST.get('email', '')
            emp.address = request.POST.get('address', '')
            emp.joining_date = request.POST['joining_date']
            emp.designation = request.POST.get('designation', '')
            emp.department = request.POST.get('department', 'labour')
            emp.employee_type = request.POST.get('employee_type', 'labour')
            emp.salary = request.POST.get('salary') or 0
            emp.status = request.POST.get('status', 'active')
            emp.notes = request.POST.get('notes', '')
            dob = request.POST.get('date_of_birth')
            emp.date_of_birth = dob if dob else None
            proj_id = request.POST.get('assigned_project')
            emp.assigned_project_id = proj_id if proj_id else None
            if request.FILES.get('profile_photo'):
                emp.profile_photo = request.FILES['profile_photo']
            emp.save()
            messages.success(request, f'Worker "{emp.full_name}" updated.')
            return redirect('employees:detail', pk=emp.pk)
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'employees/form.html', {
        'page_title': 'Edit Worker', 'emp': emp, 'projects': projects,
        'type_choices': Employee.TYPE_CHOICES,
        'status_choices': Employee.STATUS_CHOICES,
        'dept_choices': Employee.DEPT_CHOICES,
    })


@login_required
def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = emp.full_name
        emp.delete()
        messages.success(request, f'Worker "{name}" removed.')
    return redirect('employees:list')
