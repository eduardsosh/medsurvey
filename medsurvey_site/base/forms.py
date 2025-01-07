from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from base.models import UserAdditionalData
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text=_('Email will be used for verification and password recovery.'))
    first_name = forms.CharField(required=True, max_length=256,label=_("First name"))
    last_name = forms.CharField(max_length=256, required=True,label=_("Last name"))
    personal_number = forms.CharField(max_length=12,required=True,label=_("Personal code"))
    gender = forms.ChoiceField(choices=UserAdditionalData.Gender,required=True,label=_("Gender"))
    accept = forms.BooleanField(required=True,label=_("I accept the terms and conditions"))

    class Meta:
        model = User
        fields = ("username", "email", 'first_name','last_name','gender','personal_number',"password1", "password2",'accept')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with this email already exists."))
        return email
    
    def clean_personal_number(self):
        personal_number = self.cleaned_data.get('personal_number')
        if UserAdditionalData.objects.filter(personal_code=personal_number).exists():
            raise ValidationError(_("A user with this personal code already exists."))
        return personal_number
    
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()

        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        personal_number = self.cleaned_data.get('personal_number')
        gender = self.cleaned_data.get('gender')

        UserAdditionalData.objects.create(base_user=user,
                                          first_name=first_name,
                                          last_name = last_name, 
                                          personal_code=personal_number,
                                          gender=gender)

        return user
    


class CustomUserEditForm(forms.ModelForm):
    first_name = forms.CharField(required=True, max_length=256,label=_("First name"))
    last_name = forms.CharField(max_length=256, required=True,label=_("Last name"))
    gender = forms.ChoiceField(choices=UserAdditionalData.Gender,required=True,label=_("Gender"))

    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10'
        self.helper.add_input(Submit('submit', 'Save Changes'))

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        # Now update the related UserAdditionalData
        user_additional_data = UserAdditionalData.objects.get(base_user=user)
        user_additional_data.first_name = self.cleaned_data.get('first_name')
        user_additional_data.last_name = self.cleaned_data.get('last_name')
        user_additional_data.gender = self.cleaned_data.get('gender')
        user_additional_data.save()

        return user