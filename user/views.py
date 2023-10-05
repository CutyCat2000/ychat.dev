from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, AccountSettingsForm, MfaForm
from django.contrib.auth.models import User
from server.models import Server
from channel.models import Channel
import config
import random
from mfa.models import mfaKey
import requests
from django.contrib.auth.decorators import login_required


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            try:
                mfaObject = mfaKey.objects.get(user__id=user.id)
            except:
                mfaObject = False
            if not mfaObject:
                if user is not None:
                    login(request, user)
                    return redirect('home')
            else:
                mfaForm = MfaForm(initial={
                    'username': username,
                    'password': password
                })
                return render(request, 'user/2fa_login.html',
                              {'form': mfaForm})
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})


def user_2fa_login(request):
    if request.method == 'POST':
        form = MfaForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            key = form.cleaned_data['key']
            print(username, password, key)
            user = authenticate(request, username=username, password=password)
            try:
                mfaObject = mfaKey.objects.get(user__id=user.id)
            except:
                mfaObject = False
            if not mfaObject:
                if user is not None:
                    login(request, user)
                    return redirect('home')
            else:
                real_key = requests.get("https://2fa.live/tok/" +
                                        mfaObject.key).json()["token"]
                real_key2 = requests.get(
                    "https://2fa.live/tok/" +
                    '-'.join([mfaObject.key[i:i + 4]
                              for i in range(0, 16, 4)])).json()["token"]
                if key == real_key or key == real_key2:
                    login(request, user)
                    return redirect('home')

    return redirect('user:login')


@login_required
def user_logout(request):
    logout(request)
    return redirect('user:login')


def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password = form.cleaned_data['password'])
                for server_id in [1]:
                    try:
                        server = Server.objects.get(id=server_id)
                    except:
                        server = Server.objects.create(
                            name="Default Server | DO NOT DELETE",
                            icon=config.ICON,
                            owner=user,
                        )
                        server.admins.add(user)
                        rules_channel = Channel.objects.create(
                            name="rules",
                            default_perm_write=False,
                            position=1,
                        )
                        chat_channel = Channel.objects.create(
                            name="chat",
                            default_perm_write=True,
                            position=2,
                        )
                        server.channels.add(chat_channel, rules_channel)
                    if user.id == 1:
                        user.is_staff = True
                        user.is_admin = True
                        user.is_superuser = True
                        user.save()
                    user.servers.add(server)
                    server.users.add(user)
                login(request, user)
                return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'user/register.html', {'form': form})


@login_required
def settings(request):
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            #email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if username.strip() and password.strip():
                if username.strip() and password.strip():
                    request.user.username = username
                    #request.user.email = email
                    request.user.set_password(password)
                    request.user.save()
                    user = authenticate(username=username, password=password)
                    login(request, user)
            return redirect('home')
    else:
        form = AccountSettingsForm(initial={
            'username': request.user.username,
            #'email': request.user.email,
        })
    try:
        mfaKey.objects.get(user__id=request.user.id)
        has2fa = True
    except:
        has2fa = False
    return render(request,
                  'user/settings.html',
                  context={
                      "form": form,
                      "has2fa": has2fa
                  })


@login_required
def enable_2fa(request):
    try:
        mfaObject = mfaKey.objects.get(user__id=request.user.id)
    except:
        secret_key = "".join([str(random.randint(0, 9)) for _ in range(16)])
        mfaObject = mfaKey.objects.create(key=secret_key, user=request.user)
    request.user.save()
    return render(request,
                  "user/enable_2fa.html",
                  context={
                      "2fa":
                      '-'.join(
                          [mfaObject.key[i:i + 4] for i in range(0, 16, 4)])
                  })


@login_required
def disable_2fa(request):
    try:
        mfaObject = mfaKey.objects.get(user__id=request.user.id)
        mfaObject.delete()
    except:
        pass
    return redirect('user:settings')
