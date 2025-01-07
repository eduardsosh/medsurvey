from .models import Notification

def unread_notification_count(request):
    """
    Returns a dictionary with the unread notifications count
    for the currently logged-in user.
    """
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            recipent=request.user,
            read=False
        ).count()
    else:
        count = 0

    return {
        'unread_notifications_count': count
    }
