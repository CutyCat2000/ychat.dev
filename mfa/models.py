from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class mfaKey(models.Model):
    key = models.CharField(max_length=16)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='user')
