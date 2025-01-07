from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.http import HttpResponse

@login_required
def notification_list(request):
    """
    Display the main notifications page:
      - Show unread notifications
      - Provide a button to load read notifications via HTMX
    """
    unread_notifications = Notification.objects.filter(
        recipent=request.user,
        read=False
    ).order_by('-time_created')

    context = {
        'unread_notifications': unread_notifications,
    }
    return render(request, 'notifications.html', context)

@login_required
def read_notifications(request):
    """
    Return a partial snippet of read notifications,
    which is injected into the page via HTMX.
    """
    read_notifications = Notification.objects.filter(
        recipent=request.user,
        read=True
    ).order_by('-time_created')

    return render(request, 'partials/read_notifications.html', {
        'read_notifications': read_notifications
    })
    


@login_required
def mark_notification_as_read(request, notification_id):
    """
    Mark a single notification as read and return
    a simple response (or partial) to allow HTMX to update the DOM.
    """
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipent=request.user
    )
    notification.read = True
    notification.save()
    # Return an empty response so that HTMX can remove the DOM element.
    return HttpResponse("")




