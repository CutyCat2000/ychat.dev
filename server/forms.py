from django import forms
from .models import Server
from channel.models import Channel

class ServerSettingsForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'icon', 'invite','description', 'public']