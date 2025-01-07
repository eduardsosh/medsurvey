# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/read/', views.read_notifications, name='read_notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
]
