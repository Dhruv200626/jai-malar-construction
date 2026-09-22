from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count
import json, calendar


@login_required
def index(request):
    from projects.models import Project
    from employees.models import Employee
    from expenses.models import Expense
    from attendance.models import Attendance
    from materials.models import Material, MaterialTransaction

    now = timezone.now()
    this_month = {'date__year': now.year, 'date__month': now.month}

    # KPIs
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='active').count()
    completed_projects = Project.objects.filter(status='completed').count()
    total_employees = Employee.objects.filter(status='active').count()

    # Monthly costs — sourced from Expense records (material purchases auto-create these)
    approved_expenses = Expense.objects.filter(
        approval_status='approved', **this_month
    )
    monthly_cost = approved_expenses.aggregate(t=Sum('amount'))['t'] or 0
    material_cost = approved_expenses.filter(category='material').aggregate(t=Sum('amount'))['t'] or 0
    labour_cost = approved_expenses.filter(category__in=['labour', 'salary']).aggregate(t=Sum('amount'))['t'] or 0
    equipment_cost = approved_expenses.filter(category='equipment').aggregate(t=Sum('amount'))['t'] or 0
    other_cost = float(monthly_cost) - float(material_cost) - float(labour_cost) - float(equipment_cost)

    # Live inventory stats
    active_materials = Material.objects.filter(is_active=True)
    total_materials = active_materials.count()
    low_stock_items = [m for m in active_materials if m.is_low_stock]
    low_stock_count = len(low_stock_items)
    total_stock_value = sum(float(m.stock_value) for m in active_materials)

    # Upcoming / active projects
    upcoming_projects = Project.objects.filter(
        status__in=['active', 'upcoming']
    ).select_related('client')[:6]

    # Monthly expense trend (last 6 months)
    monthly_labels = []
    monthly_data = []
    for i in range(5, -1, -1):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        monthly_labels.append(calendar.month_abbr[m])
        total = Expense.objects.filter(
            date__year=y, date__month=m, approval_status='approved'
        ).aggregate(t=Sum('amount'))['t'] or 0
        monthly_data.append(float(total))

    # Today's attendance summary
    today_att = Attendance.objects.filter(date=now.date())
    att_present = today_att.filter(status='present').count()
    att_absent = today_att.filter(status='absent').count()

    return render(request, 'dashboard/index.html', {
        'page_title': 'Dashboard',
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_employees': total_employees,
        'monthly_cost': monthly_cost,
        'material_cost': material_cost,
        'labour_cost': labour_cost,
        'equipment_cost': equipment_cost,
        'other_cost': max(0, other_cost),
        'upcoming_projects': upcoming_projects,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'att_present': att_present,
        'att_absent': att_absent,
        'current_time': now,
        'total_materials': total_materials,
        'low_stock_count': low_stock_count,
        'low_stock_items': low_stock_items[:5],
        'total_stock_value': total_stock_value,
    })
