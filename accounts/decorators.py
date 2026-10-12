"""
Custom decorators for access control.
Only the admin user (hemantmohite071193@gmail.com) can write/edit/delete data.
All other users can only view data.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

ADMIN_EMAIL = 'hemantmohite071193@gmail.com'


def admin_required(view_func):
    """
    Restricts a view to admin only (hemantmohite071193@gmail.com).
    Other logged-in users are redirected with an access denied message.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.email.lower() != ADMIN_EMAIL.lower():
            messages.error(
                request,
                'Access denied. Only the admin can perform this action.'
            )
            return redirect(request.META.get('HTTP_REFERER', 'dashboard:index'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
