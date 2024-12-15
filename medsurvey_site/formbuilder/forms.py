from django import forms
from django.forms import ModelForm
from .models import Form
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class FormCreationForm(ModelForm):
    class Meta:
        model = Form
        fields = [
            'title',
            'description',
            'start_date',
            'end_date',
            'interval',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        today = datetime.date.today()

        # Ensure start_date is not in the past
        if start_date and start_date < today:
            self.add_error('start_date', _("Start date cannot be in the past."))

        # Ensure end_date is not in the past
        if end_date and end_date < today:
            self.add_error('end_date', _("End date cannot be in the past."))

        # Ensure end_date is not before start_date
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', _("End date cannot be before the start date."))


class FormEditForm(ModelForm):
    class Meta:
        model = Form
        fields = [
            'title',
            'description',
            'start_date',
            'end_date',
            'interval',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Interval should never be editable
        self.fields['interval'].disabled = True

        if self.instance and self.instance.pk is not None:
            today = datetime.date.today()
            
            # Disable start_date if it has already passed or is today
            if self.instance.start_date and self.instance.start_date <= today:
                self.fields['start_date'].disabled = True
            
            # Disable end_date if it has already passed or is today
            if self.instance.end_date and self.instance.end_date <= today:
                self.fields['end_date'].disabled = True
