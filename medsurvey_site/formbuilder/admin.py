from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserForms, Form

@admin.register(UserForms)
class UserFormsAdmin(admin.ModelAdmin):
    list_display = ('user', 'form')
    search_fields = ('user__username', 'form__id')  # Adjust fields as needed
    
@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'creation_date_time', 'interval', 'start_date', 'end_date')
    list_filter = ('interval', 'author', 'creation_date_time')
    search_fields = ('title', 'author__username', 'description')
    ordering = ('-creation_date_time',)
    readonly_fields = ('creation_date_time',)
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "description", "author")
        }),
        ("Schedule", {
            "fields": ("start_date", "end_date", "interval")
        }),
        ("Metadata", {
            "fields": ("creation_date_time",),
            "classes": ("collapse",)  # Makes this section collapsible
        }),
    )
    
    
from django.contrib import admin
from .models import Answer

from django.contrib import admin
from .models import Answer

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'submission', 'field', 'masked_answer', 'creation_date')
    list_filter = ('user', 'submission', 'creation_date')
    search_fields = ('user__username', 'submission__id', 'field__question_text')  # Assuming Question has `question_text`
    
    # Make all fields readonly
    readonly_fields = ('user', 'submission', 'field', 'answer', 'creation_date')

    def masked_answer(self, obj):
        return '***'
    
    masked_answer.short_description = 'Answer'  

    # Prevent any changes (disable editing & adding new entries)
    def has_add_permission(self, request):
        return False  # Disables the "Add" button

    def has_change_permission(self, request, obj=None):
        return False  # Prevents editing existing objects

    def has_delete_permission(self, request, obj=None):
        return False  # Prevents deletion of objects

