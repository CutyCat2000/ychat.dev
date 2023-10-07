from django.db import models
from message.models import Message


class Channel(models.Model):
    name = models.CharField(max_length=12)
    messages = models.ManyToManyField(Message, related_name='messages')
    id = models.AutoField(primary_key=True)
    default_perm_write = models.BooleanField(default=True)
    position = models.IntegerField()

    # admin_perm_write = models.BooleanField(default = True)

    def __str__(self):
        return self.name

