from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'placeholder': 'Password',
        }))
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())


class MfaForm(forms.Form):
    key = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': '6 digit 2fa key.'}))
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Password'}))


class RegisterForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username - Max: 25'}),
        max_length=25)
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible())


class AccountSettingsForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    #email = forms.EmailField(required=False)
