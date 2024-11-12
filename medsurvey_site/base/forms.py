from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from base.models import UserAdditionalData

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text=_('Email will be used for verification and password recovery.'))
    first_name = forms.CharField(required=True, max_length=256,label=_("First name"))
    last_name = forms.CharField(max_length=256, required=True,label=_("Last name"))
    personal_number = forms.CharField(max_length=12,required=True,label=_("Personal code"))
    gender = forms.ChoiceField(choices=UserAdditionalData.Gender,required=True,label=_("Gender"))

    class Meta:
        model = User
        fields = ("username", "email", 'first_name','last_name','gender','personal_number',"password1", "password2")

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