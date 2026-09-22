from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Client


@login_required
def client_list(request):
    qs = Client.objects.all().order_by('name')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(company__icontains=q) | Q(phone__icontains=q))
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'clients/list.html', {'page_title': 'Clients', 'clients': page, 'q': q})


@login_required
def client_add(request):
    if request.method == 'POST':
        try:
            c = Client()
            c.name = request.POST['name']
            c.company = request.POST.get('company', '')
            c.phone = request.POST['phone']
            c.email = request.POST.get('email', '')
            c.address = request.POST.get('address', '')
            c.gst_number = request.POST.get('gst_number', '')
            c.notes = request.POST.get('notes', '')
            c.save()
            messages.success(request, f'Client "{c.name}" added.')
            return redirect('clients:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'clients/form.html', {'page_title': 'Add Client'})


@login_required
def client_edit(request, pk):
    c = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        try:
            c.name = request.POST['name']
            c.company = request.POST.get('company', '')
            c.phone = request.POST['phone']
            c.email = request.POST.get('email', '')
            c.address = request.POST.get('address', '')
            c.gst_number = request.POST.get('gst_number', '')
            c.notes = request.POST.get('notes', '')
            c.save()
            messages.success(request, f'Client "{c.name}" updated.')
            return redirect('clients:list')
        except Exception as ex:
            messages.error(request, f'Error: {str(ex)}')
    return render(request, 'clients/form.html', {'page_title': 'Edit Client', 'client': c})


@login_required
def client_delete(request, pk):
    c = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        c.delete()
        messages.success(request, f'Client deleted.')
    return redirect('clients:list')
