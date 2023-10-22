from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import LoginForm, RegisterForm, AccountSettingsForm, MfaForm
from django.contrib.auth.models import User
from server.models import Server
from channel.models import Channel
import config
import random
from mfa.models import mfaKey
import requests
from django.contrib.auth.decorators import login_required
from .models import RegisteredIP


def get_client_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        return request.META['REMOTE_ADDR']


def is_ip_within_limit(ip_address):
    try:
        registered_ip = RegisteredIP.objects.get(ip_address=ip_address)
        return registered_ip.amount < config.MAX_PER_IP
    except RegisteredIP.DoesNotExist:
        return True


def is_ip_detected(ip):
    req = requests.get("https://v2.api.iphub.info/guest/ip/" + ip + "?c=" +
                       str(random.randint(0, 9999999999999))).json()
    if req["block"]:
        return True
    return False


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
                    try:
                        next_url = request.GET["next"]
                        return HttpResponseRedirect(
                            f"https://{config.WEBSITE}" + next_url)
                    except:
                        return redirect("home")
            else:
                mfaForm = MfaForm(initial={
                    'username': username,
                    'password': password
                })
                return render(request, 'user/2fa_login.html',
                              {'form': mfaForm,"theme": config.DEFAULT_THEME})
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form, "theme": config.DEFAULT_THEME})


def user_2fa_login(request):
    if request.method == 'POST':
        form = MfaForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            key = form.cleaned_data['key']
            user = authenticate(request, username=username, password=password)
            try:
                mfaObject = mfaKey.objects.get(user__id=user.id)
            except:
                mfaObject = False
            if not mfaObject:
                if user is not None:
                    login(request, user)
                    try:
                        next_url = request.GET["next"]
                        return HttpResponseRedirect(
                            f"https://{config.WEBSITE}" + next_url)
                    except:
                        return redirect("home")
            else:
                real_key = requests.get("https://2fa.live/tok/" +
                                        mfaObject.key).json()["token"]
                real_key2 = requests.get(
                    "https://2fa.live/tok/" +
                    '-'.join([mfaObject.key[i:i + 4]
                              for i in range(0, 16, 4)])).json()["token"]
                if key == real_key or key == real_key2:
                    login(request, user)
                    next_url = request.POST.get('next', '')
                    try:
                        next_url = request.GET["next"]
                        return HttpResponseRedirect(
                            f"https://{config.WEBSITE}" + next_url)
                    except:
                        return redirect("home")

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
            client_ip = get_client_ip(request)

            if not User.objects.filter(username=username).exists():
                if config.ALLOW_VPN == False:
                    try:
                        if is_ip_detected(client_ip):
                            return render(request, "user/vpnfound.html", {"theme": config.DEFAULT_THEME})
                    except Exception as es:
                        print(es)
                if is_ip_within_limit(client_ip):
                    user = User.objects.create_user(
                        username=username,
                        password=form.cleaned_data['password'])

                    # Increase the amount for the IP address
                    registered_ip, created = RegisteredIP.objects.get_or_create(
                        ip_address=client_ip)
                    if created:
                        registered_ip.amount = 1
                    else:
                        registered_ip.amount += 1
                    registered_ip.save()
                else:
                    return render(request, "user/alreadyregistered.html", {"theme": config.DEFAULT_THEME, })
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
                    return render(
                        request, 'user/register.html', {
                            'form':
                            form,
                            'error_message':
                            'IP address has reached the maximum allowed registrations.',
                            "theme": config.DEFAULT_THEME,
                        })
            else:
                return render(request, 'user/register.html', {
                    'form': form,
                    'error_message': 'Username already exists.',
                    "theme": config.DEFAULT_THEME,
                })
    else:
        form = RegisterForm()

    return render(request, 'user/register.html', {'form': form, "theme": config.DEFAULT_THEME, })


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
                      "has2fa": has2fa,
                      "theme": config.DEFAULT_THEME,
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
                          [mfaObject.key[i:i + 4] for i in range(0, 16, 4)]),
                      "theme": config.DEFAULT_THEME,
                  })


@login_required
def disable_2fa(request):
    try:
        mfaObject = mfaKey.objects.get(user__id=request.user.id)
        mfaObject.delete()
    except:
        pass
    return redirect('user:settings')
