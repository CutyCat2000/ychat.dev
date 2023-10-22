from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    content = models.CharField(max_length=265)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='message_author')
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    reactions = models.ManyToManyField('Reaction',
                                       related_name='message_reactions')

    def __str__(self):
        return self.content


class Reaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20)
    users = models.ManyToManyField(User, related_name='reactions')

    def __str__(self):
        return f"Reactions of type '{self.reaction_type}' to '{self.message.content}'"
