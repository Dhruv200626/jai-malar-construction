from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import DailyReport
from projects.models import Project
from expenses.models import Expense
from attendance.models import Attendance
import json


@login_required
def daily_reports(request):
    qs = DailyReport.objects.select_related('project', 'submitted_by').order_by('-report_date')
    project_id = request.GET.get('project', '')
    if project_id:
        qs = qs.filter(project_id=project_id)
    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'reports/daily.html', {
        'page_title': 'Daily Reports', 'reports': page,
        'projects': Project.objects.filter(status='active'),
        'project_id': project_id,
    })


@login_required
def daily_report_add(request):
    projects = Project.objects.filter(status='active')
    today = timezone.now().date()
    if request.method == 'POST':
        try:
            r = DailyReport()
            r.project_id = request.POST['project']
            r.report_date = request.POST.get('report_date', str(today))
            r.weather = request.POST.get('weather', 'sunny')
            r.total_workers = request.POST.get('total_workers') or 0
            r.present_workers = request.POST.get('present_workers') or 0
            r.work_completed = request.POST.get('work_completed', '')
            r.work_in_progress = request.POST.get('work_in_progress', '')
            r.materials_used = request.POST.get('materials_used', '')
            r.equipment_used = request.POST.get('equipment_used', '')
            r.issues = request.POST.get('issues', '')
            r.safety_incidents = request.POST.get('safety_incidents', '')
            r.supervisor_remarks = request.POST.get('supervisor_remarks', '')
            r.submitted_by = request.user
            r.save()
            messages.success(request, 'Daily report submitted successfully.')
            return redirect('reports:daily')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'reports/daily_form.html', {
        'page_title': 'Add Daily Report', 'projects': projects,
        'today': today, 'weather_choices': DailyReport.WEATHER_CHOICES,
    })


@login_required
def monthly_reports(request):
    from datetime import date
    projects = Project.objects.all()
    now = timezone.now()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))
    project_id = request.GET.get('project', '')

    report_data = []
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        # Attendance data
        att_qs = Attendance.objects.filter(
            project=project,
            date__year=year, date__month=month
        )
        man_days = att_qs.filter(status='present').count()
        half_days = att_qs.filter(status='half_day').count()
        total_mandays = man_days + (half_days * 0.5)

        # Cost data
        exp_qs = Expense.objects.filter(
            project=project,
            date__year=year, date__month=month,
            approval_status='approved'
        )
        cost_breakdown = {}
        for cat, label in Expense.CATEGORY_CHOICES:
            total = exp_qs.filter(category=cat).aggregate(t=Sum('amount'))['t'] or 0
            if total > 0:
                cost_breakdown[label] = float(total)

        total_cost = exp_qs.aggregate(t=Sum('amount'))['t'] or 0

        report_data = {
            'project': project,
            'man_days': total_mandays,
            'total_cost': total_cost,
            'cost_breakdown': cost_breakdown,
            'labour_cost': exp_qs.filter(category__in=['labour', 'salary']).aggregate(t=Sum('amount'))['t'] or 0,
            'material_cost': exp_qs.filter(category='material').aggregate(t=Sum('amount'))['t'] or 0,
            'equipment_cost': exp_qs.filter(category='equipment').aggregate(t=Sum('amount'))['t'] or 0,
            'other_cost': exp_qs.exclude(category__in=['labour', 'salary', 'material', 'equipment']).aggregate(t=Sum('amount'))['t'] or 0,
        }

    years = range(now.year - 2, now.year + 2)
    months = [
        (1,'January'),(2,'February'),(3,'March'),(4,'April'),
        (5,'May'),(6,'June'),(7,'July'),(8,'August'),
        (9,'September'),(10,'October'),(11,'November'),(12,'December')
    ]
    return render(request, 'reports/monthly.html', {
        'page_title': 'Monthly Reports', 'projects': projects,
        'report_data': report_data, 'month': month, 'year': year,
        'project_id': project_id, 'years': years, 'months': months,
        'month_name': dict(months).get(month, ''),
    })


@login_required
def analytics(request):
    from datetime import date, timedelta
    import calendar

    now = timezone.now()

    # Last 6 months expense data
    monthly_labels = []
    monthly_data = []
    for i in range(5, -1, -1):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        label = calendar.month_abbr[m]
        monthly_labels.append(label)
        total = Expense.objects.filter(
            date__year=y, date__month=m, approval_status='approved'
        ).aggregate(t=Sum('amount'))['t'] or 0
        monthly_data.append(float(total))

    # Project cost breakdown
    projects = Project.objects.filter(status__in=['active', 'completed'])
    project_names = [p.name[:20] for p in projects]
    project_costs = []
    for p in projects:
        cost = Expense.objects.filter(project=p, approval_status='approved').aggregate(t=Sum('amount'))['t'] or 0
        project_costs.append(float(cost))

    # This month summary
    this_month_total = Expense.objects.filter(
        date__year=now.year, date__month=now.month, approval_status='approved'
    ).aggregate(t=Sum('amount'))['t'] or 0

    cat_data = {}
    for cat, label in Expense.CATEGORY_CHOICES:
        total = Expense.objects.filter(
            date__year=now.year, date__month=now.month,
            approval_status='approved', category=cat
        ).aggregate(t=Sum('amount'))['t'] or 0
        if total > 0:
            cat_data[label] = float(total)

    return render(request, 'reports/analytics.html', {
        'page_title': 'Analytics',
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'project_names': json.dumps(project_names),
        'project_costs': json.dumps(project_costs),
        'this_month_total': this_month_total,
        'cat_data': json.dumps(cat_data),
        'cat_labels': json.dumps(list(cat_data.keys())),
        'cat_values': json.dumps(list(cat_data.values())),
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(status='active').count(),
    })
