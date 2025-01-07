from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipent', 'read', 'time_created')
    list_filter = ('read', 'time_created', 'recipent')
    search_fields = ('title', 'text', 'recipent__username')
    
# admin.py
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from django.contrib.auth.models import User
from django.contrib import admin

from .models import Notification

class BulkNotificationForm(forms.Form):
    title = forms.CharField(max_length=200, required=True)
    text = forms.CharField(widget=forms.Textarea, required=True)
    mark_as_read = forms.BooleanField(required=False, label="Mark as read upon creation?")
    
    # Optionally filter users by some criteria
    # e.g. active users only
    # or add a multiple-choice user selection field

def create_notifications_for_all_users(title, text, mark_as_read=False):
    # This is a utility function to create notifications for all active users:
    all_users = User.objects.filter(is_active=True)
    notifications = []
    for user in all_users:
        notifications.append(
            Notification(
                user=user,       # or set an explicit “admin user” as the sender
                recipent=user,   # the same user as recipient
                title=title,
                text=text,
                read=mark_as_read,
            )
        )
    # Bulk create for efficiency
    Notification.objects.bulk_create(notifications)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Normal Notification admin + a custom "Bulk Create" admin view
    """
    list_display = ('title', 'recipent', 'read', 'time_created')
    list_filter = ('read', 'time_created', 'recipent')
    search_fields = ('title', 'text', 'recipent__username')

    # 1) Add a special URL pattern for the new "bulk create" form
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('bulk-create/', self.admin_site.admin_view(self.bulk_create_view), name='bulk_create_notifications'),
        ]
        return my_urls + urls

    # 2) The actual view that handles "bulk create"
    def bulk_create_view(self, request):
        if request.method == 'POST':
            form = BulkNotificationForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data['title']
                text = form.cleaned_data['text']
                mark_as_read = form.cleaned_data['mark_as_read']
                # Create notifications for all (or subset) users
                create_notifications_for_all_users(title, text, mark_as_read)
                self.message_user(request, "Bulk notifications created successfully.")
                return redirect('..')  # Go back to the Notification list
        else:
            form = BulkNotificationForm()

        context = {
            **self.admin_site.each_context(request),
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/bulk_create_notifications.html', context)
