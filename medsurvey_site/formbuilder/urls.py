# myapp/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('create-form/', views.create_form, name='create_form'),
    path('my-created-forms/', views.view_created_forms, name='view_created_forms'),
    path('form/<int:pk>/edit/', views.edit_form, name='edit_form'),
]
