import uuid
from django.db import models
from django.contrib.auth.models import User
from channel.models import Channel


def image_upload_path(instance, filename):
    # Generate a UUID for the filename
    filename = f"{uuid.uuid4().hex}.png"
    # Return the upload path
    return f"media/{filename}"


class Server(models.Model):
    name = models.CharField(max_length=25)
    icon = models.ImageField(upload_to=image_upload_path)
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='owned_servers')
    admins = models.ManyToManyField(User, related_name='administered_servers')
    users = models.ManyToManyField(User, related_name='servers')
    channels = models.ManyToManyField(Channel, related_name='channels')
    id = models.AutoField(primary_key=True)
    invite = models.CharField(max_length=25, default="")
    description = models.CharField(max_length=500, default="")
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.name
