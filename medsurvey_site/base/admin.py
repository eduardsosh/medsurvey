from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from base.models import UserAdditionalData, Examiner

class UserProfileInline(admin.StackedInline):
    model = UserAdditionalData
    can_delete = False
    verbose_name_plural = 'Additional data'
    fields = ('personal_code','gender')

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('useradditionaldata')
        return queryset

@admin.register(Examiner)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution')  # Display fields in the admin table
    search_fields = ('user__username',)  # Enable search by User's username
    autocomplete_fields = ['user']

    # Custom method to display the related User's username in list view
    def user__username(self, obj):
        return obj.user.username
    user__username.short_description = 'Author Username'  # Label for the column


# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
