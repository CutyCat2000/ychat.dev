from django import forms
from .models import Server
from channel.models import Channel


class ServerSettingsForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'icon', 'invite', 'description', 'public']


class ChannelForm(forms.ModelForm):
    delete = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'delete-checkbox'}))

    class Meta:
        model = Channel
        fields = ['name', 'position', 'default_perm_write']
        labels = {'default_perm_write': 'Allow Messages'}
