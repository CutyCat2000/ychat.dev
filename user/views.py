from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, AccountSettingsForm
from django.contrib.auth.models import User
from server.models import Server
from channel.models import Channel


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(
                    'home')
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('user:login')


def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username)
                for server_id in [1]:
                    try:
                      server = Server.objects.get(id=server_id)
                    except:
                      server = Server.objects.create(
                          name="Default Server | DO NOT DELETE",
                          icon="static/icon.png",
                          owner=user,)
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
                return redirect(
                    'home')
    else:
        form = RegisterForm()

    return render(request, 'user/register.html', {'form': form})


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
            return redirect('home'
                            )
    else:
        form = AccountSettingsForm(initial={
            'username': request.user.username,
            #'email': request.user.email,
        })
    return render(request, 'user/settings.html', context={"form": form})
