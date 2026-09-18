from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Expense
from projects.models import Project


@login_required
def expense_list(request):
    qs = Expense.objects.select_related('project', 'created_by').order_by('-date')
    q = request.GET.get('q', '')
    cat = request.GET.get('category', '')
    status = request.GET.get('status', '')
    project_id = request.GET.get('project', '')
    if q:
        qs = qs.filter(Q(description__icontains=q) | Q(vendor__icontains=q))
    if cat:
        qs = qs.filter(category=cat)
    if status:
        qs = qs.filter(approval_status=status)
    if project_id:
        qs = qs.filter(project_id=project_id)

    total = qs.aggregate(t=Sum('amount'))['t'] or 0
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'expenses/list.html', {
        'page_title': 'Expenses', 'expenses': page,
        'q': q, 'cat': cat, 'status': status,
        'total': total,
        'projects': Project.objects.filter(status__in=['active', 'upcoming']),
        'categories': Expense.CATEGORY_CHOICES,
        'approval_choices': Expense.APPROVAL_CHOICES,
    })


@login_required
def expense_add(request):
    projects = Project.objects.filter(status__in=['active', 'upcoming'])
    if request.method == 'POST':
        try:
            e = Expense()
            e.category = request.POST['category']
            e.amount = request.POST['amount']
            e.date = request.POST['date']
            e.vendor = request.POST.get('vendor', '')
            e.payment_method = request.POST.get('payment_method', 'cash')
            e.description = request.POST.get('description', '')
            e.approval_status = 'pending'
            e.created_by = request.user
            proj_id = request.POST.get('project')
            e.project_id = proj_id if proj_id else None
            if request.FILES.get('receipt'):
                e.receipt = request.FILES['receipt']
            e.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('expenses:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'expenses/form.html', {
        'page_title': 'Add Expense', 'projects': projects,
        'categories': Expense.CATEGORY_CHOICES,
        'payment_choices': Expense.PAYMENT_CHOICES,
        'today': timezone.now().date(),
    })


@login_required
def expense_edit(request, pk):
    exp = get_object_or_404(Expense, pk=pk)
    projects = Project.objects.filter(status__in=['active', 'upcoming'])
    if request.method == 'POST':
        try:
            exp.category = request.POST['category']
            exp.amount = request.POST['amount']
            exp.date = request.POST['date']
            exp.vendor = request.POST.get('vendor', '')
            exp.payment_method = request.POST.get('payment_method', 'cash')
            exp.description = request.POST.get('description', '')
            proj_id = request.POST.get('project')
            exp.project_id = proj_id if proj_id else None
            if request.FILES.get('receipt'):
                exp.receipt = request.FILES['receipt']
            exp.save()
            messages.success(request, 'Expense updated.')
            return redirect('expenses:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'expenses/form.html', {
        'page_title': 'Edit Expense', 'exp': exp, 'projects': projects,
        'categories': Expense.CATEGORY_CHOICES,
        'payment_choices': Expense.PAYMENT_CHOICES,
    })


@login_required
def expense_approve(request, pk):
    exp = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            exp.approval_status = 'approved'
            exp.approved_by = request.user
            messages.success(request, 'Expense approved.')
        elif action == 'reject':
            exp.approval_status = 'rejected'
            messages.warning(request, 'Expense rejected.')
        exp.save()
    return redirect('expenses:list')


@login_required
def expense_delete(request, pk):
    exp = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        exp.delete()
        messages.success(request, 'Expense deleted.')
    return redirect('expenses:list')
