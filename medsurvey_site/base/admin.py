from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from base.models import UserAdditionalData, Examiner


@admin.register(Examiner)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution')  # Display fields in the admin table
    search_fields = ('user__username',)  # Enable search by User's username
    autocomplete_fields = ['user']

    # Custom method to display the related User's username in list view
    def user__username(self, obj):
        return obj.user.username
    user__username.short_description = 'Author Username'  # Label for the column


