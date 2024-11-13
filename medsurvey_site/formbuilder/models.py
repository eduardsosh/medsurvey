from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Form(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField()


class UserForms(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)

class Field(models.Model):
    field_name = models.CharField(max_length=200)

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    answer = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

