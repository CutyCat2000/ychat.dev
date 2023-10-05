from django.shortcuts import render, redirect, get_object_or_404
from server.models import Server
from .models import Channel
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from message.models import Message, Reaction
from django.utils.safestring import mark_safe
from django.utils.html import escape
from dm.models import DM
import emoji
import re
import config
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


def replace_url(match):
    url = match.group(0)
    target = "_self" if config.WEBSITE in url else "_blank"
    return f'<a href="{url}" target="{target}">{url}</a>'


# Create your views here.
def home(request, server_id, channel_id):
    try:
        server = Server.objects.get(id=server_id)
        channel = Channel.objects.get(id=channel_id)
        messages = channel.messages.order_by('-timestamp')[:100]
        for message in messages:
            message.content = mark_safe(
                escape(
                    emoji.emojize(message.content,
                                  language="alias",
                                  variant="emoji_type"))).replace(
                                      "\\n", "<br>").replace("\n", "<br>")
            message.content = re.sub(
                "(https?://(?:www\.)?" + config.WEBSITE + "/\S*|https?://\S+)",
                replace_url, message.content)
            for reaction in message.reactions.all():
                reaction.reaction_type = emoji.emojize(
                    reaction.reaction_type)[:1]
                reaction.save()
        if request.user in server.users.all():
            context = {
                "server": {
                    "id": server_id,
                    "name": server.name,
                    "icon": server.icon,
                    "obj": server,
                    "owner_id": server.owner.id
                },
                "channel": {
                    "id": channel_id,
                    "name": channel.name,
                    "messages": messages,
                    "obj": channel
                },
                "channels": server.channels.order_by("position")
            }
            return render(request, 'index.html', context=context)
        else:
            return redirect("home")
    except Exception as es:
        print(es)
        return redirect("home")


from django.http import JsonResponse
from django.utils.html import mark_safe, escape

# ...


def updateMessages(request, user_id):
    user = User.objects.get(id=user_id)
    servers = user.servers.all()
    serverList = []
    for server in range(len(servers)):
        serverList.append({"server_id": servers[server].id, "channels": []})
        channels = servers[server].channels.all()
        for channel in channels:
            try:
                serverList[server]["channels"].append({
                    "id":
                    channel.id,
                    "message_id":
                    channel.messages.order_by('-timestamp').first().id
                })
            except:
                pass
    dmList = []
    dms = DM.objects.filter(user_1=user) | DM.objects.filter(user_2=user)
    for dm in dms.all():
        try:
            dmList.append({
                "id":
                dm.id,
                "message_id":
                dm.messages.order_by('-timestamp').first().id
            })
        except:
            pass
    return JsonResponse({"servers": serverList, "dms": dmList})


def latestMessage(request, server_id, channel_id):
    if server_id != "dm":
        # For regular server channels
        try:
            channel = Channel.objects.get(id=channel_id)
            message = channel.messages.order_by('-timestamp').first()
            if message:
                data = {"id": message.id}
                return JsonResponse(data)
            else:
                return JsonResponse({"error": "No message in this channel."})
        except Exception as es:
            print(es)
            return JsonResponse(
                {"error": "Error occurred while fetching the latest message."})
    else:
        # For DM channels
        dm_id = int(channel_id)
        try:
            dm = DM.objects.get(pk=dm_id)
            # Check if the current user is one of the users in the DM
            if request.user not in [dm.user_1, dm.user_2]:
                return JsonResponse({"error": "Access to this DM is denied."})

            # Get the latest message in the DM
            message = dm.messages.order_by('-timestamp').first()
            if message:
                data = {"id": message.id}
                return JsonResponse(data)
            else:
                return JsonResponse({"error": "No message in this DM."})
        except DM.DoesNotExist:
            return JsonResponse({"error": "DM not found."})
        except Exception as es:
            print(es)
            return JsonResponse({
                "error":
                "Error occurred while fetching the latest message in DM."
            })


def fetchMessage(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        message_content = mark_safe(
            escape(
                emoji.emojize(message.content,
                              language="alias",
                              variant="emoji_type"))).replace("\\n",
                                                              "<br>").replace(
                                                                  "\n", "<br>")
        message_content = re.sub(
            "(https?://(?:www\.)?" + config.WEBSITE + "/\S*|https?://\S+)",
            replace_url, message_content)
        data = {
            "message": {
                "id": message.id,
                "content": message_content,
                "author": {
                    "name": message.author.username,
                    "id": message.author.id
                },
                "timestamp": message.timestamp
            }
        }
        return JsonResponse(data)
    except:
        return JsonResponse({"error": "Message not found."})


def sendMessage(request, server_id, channel_id):
    if server_id != "dm":
        server_id = int(server_id)
        try:
            server = Server.objects.get(id=server_id)
            if request.user in server.users.all():
                timestamp_limit = timezone.now() - timedelta(seconds=config.MESSAGE_DELAY)
                recent_message_count = Message.objects.filter(
                    author=request.user,
                    timestamp__gte=timestamp_limit,
                ).count()

                if recent_message_count >= config.MESSAGE_LIMIT:
                    return JsonResponse(
                        {
                            "error":
                            f"Message limit reached. Please wait {config.MESSAGE_DELAY} seconds per "+str(config.MESSAGE_LIMIT) + " messages."
                        },
                        status=429)

                message_content = request.GET.get("content")
                channel = Channel.objects.get(id=channel_id)
                if channel.default_perm_write == False and not request.user.id == server.owner.id:
                    return JsonResponse({
                        "error":
                        "No permission to send messages in this channel"
                    })
                if message_content.replace(" ", "") == "":
                    return JsonResponse(
                        {"error": "Can not send an empty message"})
                message = Message.objects.create(content=message_content,
                                                 author=request.user)
                channel.messages.add(message)
                return HttpResponseRedirect(
                    f"/channel/{server_id}/{channel_id}")
            else:
                return JsonResponse(
                    {"error": "Can not send in unknown channels"})
        except Exception as es:
            print(es)
            return JsonResponse({"error": "Not logged in?"})


# When server_id is "dm" (for DM)
    dm_id = int(channel_id)  # Assuming channel_id represents the DM ID
    try:
        dm = DM.objects.get(pk=dm_id)
        # Check if the current user is one of the users in the DM
        if request.user not in [dm.user_1, dm.user_2]:
            return HttpResponseForbidden("Access to this DM is denied.")

        message_content = request.GET.get("content")
        if message_content.replace(" ", "") == "":
            return JsonResponse({"error": "Cannot send an empty message"})
        message = Message.objects.create(content=message_content,
                                         author=request.user)
        dm.messages.add(message)

        return HttpResponseRedirect(f"/dm/{dm_id}")
    except DM.DoesNotExist:
        return JsonResponse({"error": "DM not found."})
    except Exception as es:
        print(es)
        return JsonResponse({"error": "Error occurred while sending message."})


def editMessage(request, server_id, channel_id, message_id):
    if server_id != "dm":
        server_id = int(server_id)
        try:
            server = Server.objects.get(id=server_id)
            if request.user in server.users.all():
                message_content = request.GET.get("content")
                channel = Channel.objects.get(id=channel_id)
                message = Message.objects.get(id=message_id)
                if message.author.id != request.user.id:
                    return JsonResponse({"error": "This is not your message"})
                if channel.default_perm_write == False and not request.user.id == server.owner.id:
                    return JsonResponse({
                        "error":
                        "No permission to send messages in this channel"
                    })
                if message_content.replace(" ", "") == "":
                    return JsonResponse(
                        {"error": "Can not send empty message"})
                message.content = message_content
                message.edited = True
                message.save()
                return HttpResponseRedirect(
                    f"/channel/{server_id}/{channel_id}")
            else:
                return JsonResponse(
                    {"error": "Can not send in unknown channels"})
        except Exception as es:
            print(es)
            return JsonResponse({"error": "Not logged in?"})


# When server_id is "dm" (for DM)
    dm_id = int(channel_id)  # Assuming channel_id represents the DM ID
    try:
        dm = DM.objects.get(pk=dm_id)
        # Check if the current user is one of the users in the DM
        if request.user not in [dm.user_1, dm.user_2]:
            return HttpResponseForbidden("Access to this DM is denied.")

        message_content = request.GET.get("content")
        if message_content.replace(" ", "") == "":
            return JsonResponse({"error": "Cannot send an empty message"})

        # Create the message and associate it with the DM
        message = Message.objects.get(id=message_id)
        message.content = message_content
        message.save()

        return HttpResponseRedirect(f"/dm/{dm_id}")
    except DM.DoesNotExist:
        return JsonResponse({"error": "DM not found."})
    except Exception as es:
        print(es)
        return JsonResponse({"error": "Error occurred while sending message."})


def deleteMessage(request, server_id, channel_id, message_id):
    if server_id != "dm":
        server_id = int(server_id)
        try:
            server = Server.objects.get(id=server_id)
            if request.user in server.users.all():
                channel = Channel.objects.get(id=channel_id)
                message = Message.objects.get(id=message_id)
                if message.author.id != request.user.id and request.user.id != server.owner.id:
                    return JsonResponse(
                        {"error": "You can not delete this message"})
                message.delete()
                return HttpResponseRedirect(
                    f"/channel/{server_id}/{channel_id}")
            else:
                return JsonResponse(
                    {"error": "Can not send in unknown channels"})
        except Exception as es:
            print(es)
            return JsonResponse({"error": "Not logged in?"})


# When server_id is "dm" (for DM)
    dm_id = int(channel_id)  # Assuming channel_id represents the DM ID
    try:
        dm = DM.objects.get(pk=dm_id)
        # Check if the current user is one of the users in the DM
        if request.user not in [dm.user_1, dm.user_2]:
            return HttpResponseForbidden("Access to this DM is denied.")

        message_content = request.GET.get("content")
        if message_content.replace(" ", "") == "":
            return JsonResponse({"error": "Cannot send an empty message"})

        # Create the message and associate it with the DM
        message = Message.objects.get(id=message_id)
        message.delete()

        return HttpResponseRedirect(f"/dm/{dm_id}")
    except DM.DoesNotExist:
        return JsonResponse({"error": "DM not found."})
    except Exception as es:
        print(es)
        return JsonResponse({"error": "Error occurred while sending message."})


def updateReaction(request, message_id, reaction_type, server_id, channel_id):
    message = get_object_or_404(Message, pk=message_id)
    supported_emojis = ["💛", "👍", "👎", "👋", "❎", "✅"]
    if reaction_type not in supported_emojis:
        return JsonResponse({'error': 'Unsupported reaction type'}, status=400)
    user = request.user
    reaction, created = Reaction.objects.get_or_create(
        message=message, reaction_type=reaction_type)

    if created:
        reaction.users.add(user)
        message.reactions.add(reaction)
        return HttpResponseRedirect("/channel/" + str(server_id) + "/" +
                                    str(channel_id))
    else:
        if user in reaction.users.all():
            reaction.users.remove(user)
            if len(reaction.users.all()) == 0:
                reaction.delete()
            return HttpResponseRedirect("/channel/" + str(server_id) + "/" +
                                        str(channel_id))
        else:
            reaction.users.add(user)
            return HttpResponseRedirect("/channel/" + str(server_id) + "/" +
                                        str(channel_id))
