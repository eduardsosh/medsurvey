from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserForms

@admin.register(UserForms)
class UserFormsAdmin(admin.ModelAdmin):
    list_display = ('user', 'form')
    search_fields = ('user__username', 'form__id')  # Adjust fields as needed