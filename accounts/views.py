"""
Accounts - Views: Login, Logout, Profile, Error pages
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import LoginForm, UserCreateForm, ProfileUpdateForm
from .models import User, Role


def login_view(request):
    """Professional login page"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            remember_me = form.cleaned_data.get('remember_me', False)

            login(request, user)

            if not remember_me:
                request.session.set_expiry(0)  # Session expires on browser close

            messages.success(request, f'Welcome back, {user.first_name or user.username}!')

            # Role-based redirect
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:index')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logout and redirect to login"""
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile page"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def users_list(request):
    """User management - Admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:index')

    users = User.objects.select_related('role').order_by('-created_at')
    return render(request, 'accounts/users_list.html', {'users': users})


@login_required
def user_create(request):
    """Create new user - Admin only"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.full_name} created successfully.')
            return redirect('accounts:users_list')
    else:
        form = UserCreateForm()

    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Add User'})


# Error Handlers
def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)
