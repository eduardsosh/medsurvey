from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from base.models import UserAdditionalData

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

# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserAdditionalData)
