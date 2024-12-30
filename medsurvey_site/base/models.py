from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


# Create your models here.

class UserAdditionalData(models.Model):
    class Gender(models.IntegerChoices):
        MALE = 0, _("Male")
        FEMALE = 1, _("Female")
        UNKWN = 2, _("Rather not say")
    base_user = models.OneToOneField(User, on_delete=models.CASCADE,null=False)
    first_name = models.CharField("First name",max_length=256, null=False, blank=False)
    last_name = models.CharField("Last name",max_length=256, null=False, blank=False)
    personal_code = models.CharField("Personal code",max_length=12, null=False, blank=False, default="000000-00000")
    gender = models.IntegerField("Gender",choices=Gender, null=False, blank=False)


class Examiner(models.Model):
    """
    Examiner table, meant as doctor too\n
    user : user one to one field
    institution : CharField of institution
    """
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING, null=False)
    institution = models.CharField(max_length=256, help_text=_("Institution that the examiner works for"), blank=True)