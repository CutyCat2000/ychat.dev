from django.shortcuts import render, redirect
from .models import Server
from channel.models import Channel
from .forms import ServerSettingsForm, ChannelForm
from django.http import HttpResponseForbidden, HttpResponse
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import config
from django.forms import modelformset_factory


# Create your views here.
@login_required
def home(request, id):
    try:
        server = Server.objects.get(id=id)
        if request.user in server.users.all():
            context = {
                "server": {
                    "id": id,
                    "name": server.name,
                    "icon": server.icon,
                },
                "channels": server.channels.order_by("position"),
                "theme": config.DEFAULT_THEME,
            }
            return render(request, 'index.html', context=context)
        else:
            return redirect("home")
    except Exception as es:
        print(es)
        return redirect("home")


@login_required
def settings(request, id):
    server = Server.objects.get(id=id)

    # Check if the user is the owner of the server
    if request.user.id != server.owner.id:
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect("/server/" + str(id))

    if request.method == 'POST':
        form = form = ServerSettingsForm(request.POST,
                                         request.FILES,
                                         instance=server)
        if form.is_valid():
            name = form.cleaned_data['name']
            icon = form.cleaned_data['icon']
            server.name = name

            if icon:
                server.icon.save(icon.name,
                                 ContentFile(icon.read()),
                                 save=True)

            server.save()
            return redirect("/server/" + str(id))
    else:
        form = ServerSettingsForm(
            initial={
                'name': server.name,
                'icon': server.icon  # Django Image Field
            },
            instance=server)
    return render(request,
                  'server/settings.html',
                  context={
                      "form": form,
                      "server": server,
                      "theme": config.DEFAULT_THEME,
                  })


@login_required
def channel_settings(request, id):
    server = Server.objects.get(id=id)

    # Check if the user is the owner of the server
    if request.user.id != server.owner.id:
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect("/server/" + str(id))

    ChannelFormSet = modelformset_factory(Channel, form=ChannelForm, extra=0)

    if request.method == 'POST':
        formset = ChannelFormSet(request.POST, queryset=server.channels.all())
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data.get('delete'):
                    channel_id = form.instance.id
                    Channel.objects.filter(id=channel_id).delete()
                else:
                    form.save()
            return redirect("/server/" + str(id))
    else:
        queryset = server.channels.all()
        formset = ChannelFormSet(queryset=queryset)

    return render(request, 'server/channel_settings.html', {
        'formset': formset,
        'server': server,
        "theme": config.DEFAULT_THEME,
    })


@login_required
def new(request):
    user = request.user
    server = Server.objects.create(
        name="Template Server",
        icon=config.ICON,
        owner=user,
    )
    server.admins.add(user)
    server.users.add(user)
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
    if 'HTTP_REFERER' in request.META:
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect("home")


def join(request, invite):
    try:
        server = Server.objects.get(invite=invite)
        if not request.user.is_authenticated:
            return render(request,
                          "server/embed.html",
                          context={
                              "server": server,
                              "invite": str(invite),
                              "theme": config.DEFAULT_THEME,
                          })
        request.user.servers.add(server)
        server.users.add(request.user)
        return redirect("/server/" + str(server.id))
    except Exception as es:
        print(es)
        return redirect("home")


@login_required
def delete_server(request, server_id):
    server = Server.objects.get(id=server_id)
    if request.user.id == server.owner.id:
        server.delete()
    return redirect("home")


def discoverView(request):
    servers = Server.objects.filter(public=True)
    return render(request, "discover.html", {"servers": servers,"theme": config.DEFAULT_THEME,})
