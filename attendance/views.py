from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Attendance
from employees.models import Employee
from projects.models import Project


@login_required
def attendance_list(request):
    date_filter = request.GET.get('date', str(timezone.now().date()))
    project_id = request.GET.get('project', '')
    status = request.GET.get('status', '')
    q = request.GET.get('q', '')

    qs = Attendance.objects.select_related('employee', 'project').filter(date=date_filter)
    if project_id:
        qs = qs.filter(project_id=project_id)
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(employee__full_name__icontains=q)

    summary = {
        'total': qs.count(),
        'present': qs.filter(status='present').count(),
        'absent': qs.filter(status='absent').count(),
        'half_day': qs.filter(status='half_day').count(),
        'leave': qs.filter(status='leave').count(),
    }
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'attendance/list.html', {
        'page_title': 'Attendance', 'attendances': page,
        'summary': summary, 'date_filter': date_filter,
        'projects': Project.objects.filter(status='active'),
        'status_choices': Attendance.STATUS_CHOICES,
        'q': q, 'project_id': project_id, 'status': status,
    })


@login_required
def mark_attendance(request):
    projects = Project.objects.filter(status='active')
    today = timezone.now().date()

    if request.method == 'POST':
        project_id = request.POST.get('project')
        date = request.POST.get('date', str(today))
        employee_ids = request.POST.getlist('employee_ids')
        statuses = request.POST.getlist('statuses')
        check_ins = request.POST.getlist('check_ins')
        check_outs = request.POST.getlist('check_outs')
        remarks_list = request.POST.getlist('remarks')

        saved = 0
        for i, emp_id in enumerate(employee_ids):
            try:
                att, created = Attendance.objects.update_or_create(
                    employee_id=emp_id, date=date,
                    defaults={
                        'project_id': project_id if project_id else None,
                        'status': statuses[i] if i < len(statuses) else 'present',
                        'check_in': check_ins[i] if i < len(check_ins) and check_ins[i] else None,
                        'check_out': check_outs[i] if i < len(check_outs) and check_outs[i] else None,
                        'remarks': remarks_list[i] if i < len(remarks_list) else '',
                        'marked_by': request.user.get_full_name() or request.user.username,
                    }
                )
                saved += 1
            except Exception:
                continue

        messages.success(request, f'Attendance marked for {saved} workers.')
        return redirect('attendance:list')

    # GET: load employees by project
    project_id = request.GET.get('project', '')
    employees = []
    if project_id:
        employees = Employee.objects.filter(
            assigned_project_id=project_id, status='active'
        ).order_by('full_name')
        # Pre-fill today's existing attendance
        existing = {
            a.employee_id: a
            for a in Attendance.objects.filter(
                project_id=project_id, date=today,
                employee__in=employees
            )
        }
        for emp in employees:
            emp.today_att = existing.get(emp.pk)

    return render(request, 'attendance/mark.html', {
        'page_title': 'Mark Attendance', 'projects': projects,
        'employees': employees, 'today': today,
        'selected_project': project_id,
        'status_choices': Attendance.STATUS_CHOICES,
    })


@login_required
def attendance_delete(request, pk):
    att = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        att.delete()
        messages.success(request, 'Attendance record deleted.')
    return redirect('attendance:list')
