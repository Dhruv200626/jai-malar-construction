"""
Notifications context processor - injects notification count into every template
"""


def notifications_processor(request):
    """Add unread notification count to all templates"""
    if request.user.is_authenticated:
        try:
            from .models import Notification
            unread_count = Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        except Exception:
            unread_count = 0
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}
