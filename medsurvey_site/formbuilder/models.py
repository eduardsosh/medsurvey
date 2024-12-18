from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Form(models.Model):
    class Regularity(models.IntegerChoices):
        EVERY_DAY = 0, _("Daily")
        EVERY_WEEK = 1, _("Weekly")
        EVERY_MONTH = 2, _("Monthly")
        
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    interval = models.IntegerField(choices=Regularity, null=True,blank=True)


class UserForms(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)


class Question(models.Model):
    default_dict = {}
    class QuestionType(models.IntegerChoices):
        TEXT_FIELD = 0, _("Text field")
        TEXT_AREA = 1, _("Text area")
        CHOICE = 2, _("Choice")
        MCHOICE = 3, _("Multiple choice")
    title = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=200, null=True, blank=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(null=False, blank=True)
    type = models.IntegerField(choices=QuestionType)
    mandatory = models.BooleanField()
    options = models.JSONField(null=True, default=dict, blank=True)
    
class Submission(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    field = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Sender")
    recipent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Reciever")
    time_created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, null=False)
    text = models.TextField()
    read = models.BooleanField()
    form = models.ForeignKey(Form, on_delete=models.CASCADE, null=True)
    


