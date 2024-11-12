# myapp/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('form-creator/', views.create_form, name='create_form'),
]
