from django.db import models
from formbuilder.models import Form
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Sender")
    recipent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Reciever")
    time_created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, null=False)
    text = models.TextField()
    read = models.BooleanField(default=False)  # Make sure it has a default
    # Example: tie it to a Form, or remove if not needed
    # form = models.ForeignKey(Form, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.title} -> {self.recipent} ({'read' if self.read else 'unread'})"
    
