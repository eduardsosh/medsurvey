# myapp/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('create-form/', views.create_form, name='create_form'),
    path('my-created-forms/', views.view_created_forms, name='view_created_forms'),
    path('form/<int:pk>/edit/', views.edit_form, name='edit_form'),
    path('form/<int:form_id>/edit-questions/', views.edit_questions, name='edit_questions'),
    path('form/<int:form_id>/delete/', views.delete_form, name='delete_form'),
    path('question/<int:question_id>/move-up/', views.move_question_up, name='move_question_up'),
    path('question/<int:question_id>/move-down/', views.move_question_down, name='move_question_down'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('my-forms/', views.view_my_assigned_forms, name='my-forms'),
    path('form/<int:form_id>/participants', views.view_participants, name='view_participants'),
    path('form/<int:form_id>/fill-out', views.fill_form_view, name='fill_form_view')

]
