from django.shortcuts import render, redirect
from .models import Server
from channel.models import Channel
from .forms import ServerSettingsForm
from django.http import HttpResponseForbidden, HttpResponse
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import config


# Create your views here.
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
                "channels": server.channels.order_by("position")
            }
            return render(request, 'index.html', context=context)
        else:
            return redirect("home")
    except Exception as es:
        print(es)
        return redirect("home")


def settings(request, id):
    server = Server.objects.get(id=id)

    # Check if the user is the owner of the server
    if request.user.id != server.owner.id:
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect("home")

    if request.method == 'POST':
        form = form = ServerSettingsForm(request.POST,
                                         request.FILES,
                                         instance=server)
        if form.is_valid():
            name = form.cleaned_data['name']
            icon = form.cleaned_data['icon']  # Form Image Field

            # Save the form data only if the user is the owner
            server.name = name

            if icon:  # Check if a new icon was uploaded
                # Save the icon content to the server.icon field
                server.icon.save(icon.name,
                                 ContentFile(icon.read()),
                                 save=True)

            server.save()
            return redirect('home')
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
                      "server": server
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
      return render(request, "server/embed.html", context = {"server":server})
    request.user.servers.add(server)
    server.users.add(request.user)
    return redirect("server/"+str(server.id))
  except:
    return redirect("home")

@login_required
def delete_server(request, server_id):
  server = Server.objects.get(id=server_id)
  if request.user.id == server.owner.id:
    server.delete()
  return redirect("home")