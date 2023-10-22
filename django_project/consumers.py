import json
from channels.generic.websocket import AsyncWebsocketConsumer
from message.models import Message, Reaction
from dm.models import DM
from channel.models import Channel
from channels.db import database_sync_to_async
from server.models import Server
from django.utils import timezone
from datetime import timedelta
import config
import re
import requests
from django.utils.safestring import mark_safe
from django.utils.html import escape
import emoji
from django.shortcuts import get_object_or_404


def is_valid_url(url):
    try:
        if config.WEBSITE.lower() in url.lower():
            return False
        response = requests.head(url)
        content_type = response.headers.get('content-type', '').lower()

        # Check if the content type indicates an image
        if content_type.startswith('image/'):
            return True
        else:
            return False
    except requests.RequestException:
        return False


def replace_url(match):
    url = match.group(0)
    target = "_self" if config.WEBSITE in url else "_blank"
    return f'<a href="{url}" target="{target}">{url}</a>'


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        print(user.id)
        if user.is_authenticated:
            await self.accept()
        else:
            await self.close()
        self.room_name = "test"
        self.room_group_name = f"chat_{self.room_name}"

        # Add the user to the room's group
        await self.channel_layer.group_add(self.room_group_name,
                                           self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name,
                                               self.channel_name)

    async def receive(self, text_data):
        user = self.scope['user']
        data = json.loads(text_data)
        if data["option"] == "send_message":
            if data["serverId"] != "dm":
                messageObject = await createNewMessage(user, data["message"],
                                                       data["serverId"],
                                                       data["channelId"])
                await self.channel_layer.group_send(self.room_group_name,
                                                    messageObject)
            else:
                messageObject = {
                    "type": "send_message",
                    "option": "error",
                    "userId": user.id,
                    "message": "Still working on this, sry"
                }
                await self.channel_layer.group_send(self.room_group_name,
                                                    messageObject)
        if data["option"] == "edit_message":
            messageObject = await editMessage(data["messageId"],
                                              data["message"],
                                              data["channelId"],
                                              data["serverId"], user)
            await self.channel_layer.group_send(self.room_group_name,
                                                messageObject)
        if data["option"] == "delete_message":
            messageObject = await deleteMessage(data["messageId"],
                                                data["channelId"],
                                                data["serverId"], user)
            await self.channel_layer.group_send(self.room_group_name,
                                                messageObject)
        if data["option"] == "update_reaction":
            messageObject = await updateReaction(data["messageId"],
                                                 data["reaction"],
                                                 data["channelId"],
                                                 data["serverId"], user)
            await self.channel_layer.group_send(self.room_group_name,
                                                messageObject)

    async def send_message(self, event):
        user = self.scope["user"]
        if event["option"] == "error":
            if user.id == event["userId"]:
                await self.send(
                    text_data=json.dumps({
                        "option": "error",
                        "message": event["message"],
                    }))
        else:
            if event["option"] == "send_message":
                if event["serverId"] != "dm":
                    is_in_server = await is_user_in_server(
                        user, event["serverId"])
                    if is_in_server:
                        await self.send(text_data=json.dumps({
                            "option":
                            "send_message",
                            "message":
                            event["messageId"],
                            "message_content":
                            event["message_content"],
                            "plain_message_content":
                            event["plain_message_content"],
                            "message_author": {
                                "name": event["authorName"],
                                "id": event["authorId"]
                            },
                            "channelId":
                            event["channelId"],
                            "serverId":
                            event["serverId"],
                            "timestamp":
                            event["timestamp"],
                            "serverName":
                            event["serverName"],
                            "channelName":
                            event["channelName"],
                            "attachments":
                            event["attachments"]
                        }))
            elif event["option"] == "edit_message":
                is_in_server = await is_user_in_server(user, event["serverId"])
                if is_in_server:
                    await self.send(text_data=json.dumps(
                        {
                            "option": "edit_message",
                            "messageId": event["messageId"],
                            "channelId": event["channelId"],
                            "serverId": event["serverId"],
                            "message_content": event["message"],
                            "attachments": event["attachments"]
                        }))
            elif event["option"] == "delete_message":
                is_in_server = await is_user_in_server(user, event["serverId"])
                if is_in_server:
                    await self.send(
                        text_data=json.dumps({
                            "option": "delete_message",
                            "messageId": event["messageId"],
                            "channelId": event["channelId"],
                            "serverId": event["serverId"]
                        }))
            else:
                is_in_server = await is_user_in_server(user, event["serverId"])
                if is_in_server:
                    await self.send(text_data=json.dumps(event))


@database_sync_to_async
def updateReaction(messageId, reaction, channelId, serverId, user):
    message = get_object_or_404(Message, pk=messageId)
    supported_emojis = config.EMOJIS.split(' ')
    if reaction not in supported_emojis:
        return {"type": "send_message"}
    reactionObj, created = Reaction.objects.get_or_create(
        message=message, reaction_type=reaction)
    if created:
        reactionObj.users.add(user)
        message.reactions.add(reactionObj)
        messageObject = {
            "type": "send_message",
            "option": "create_reaction",
            "messageId": messageId,
            "serverId": serverId,
            "channelId": channelId,
            "reaction": reaction,
            "counter": reactionObj.users.count()
        }
        return messageObject
    else:
        if user in reactionObj.users.all():
            reactionObj.users.remove(user)
            if len(reactionObj.users.all()) == 0:
                reactionObj.delete()
                messageObject = {
                    "type": "send_message",
                    "option": "delete_reaction",
                    "messageId": messageId,
                    "serverId": serverId,
                    "channelId": channelId,
                    "reaction": reaction
                }
                return messageObject
            messageObject = {
                "type": "send_message",
                "option": "remove_reaction",
                "messageId": messageId,
                "serverId": serverId,
                "channelId": channelId,
                "reaction": reaction,
                "counter": reactionObj.users.count()
            }
            return messageObject
        else:
            reactionObj.users.add(user)
            messageObject = {
                "type": "send_message",
                "option": "add_reaction",
                "messageId": messageId,
                "serverId": serverId,
                "channelId": channelId,
                "reaction": reaction,
                "counter": reactionObj.users.count()
            }
            return messageObject


@database_sync_to_async
def editMessage(messageId, message, channelId, serverId, user):
    server = Server.objects.get(id=serverId)
    channel = server.channels.get(id=channelId)
    msgObject = channel.messages.get(id=messageId, author=user)
    msgObject.content = message
    msgObject.edited = True
    msgObject.save()
    all_urls = re.findall(r'(https?://\S+)', message)
    message_content = mark_safe(
        escape(emoji.emojize(message,
                             language="alias", variant="emoji_type"))).replace(
                                 "\\n", "<br>").replace("\n", "<br>")
    message_content = re.sub(
        "(https?://(?:www\.)?" + config.WEBSITE + "/\S*|https?://\S+)",
        replace_url, message_content)
    messageObject = {
        "type":
        "send_message",
        "option":
        "edit_message",
        "messageId":
        messageId,
        "serverId":
        serverId,
        "channelId":
        channelId,
        "message":
        message_content,
        "attachments": [
            "https://" + config.WEBSITE + "/cdn/resize/?url=" + url
            for url in all_urls if is_valid_url(url)
        ]
    }
    return messageObject


@database_sync_to_async
def deleteMessage(messageId, channelId, serverId, user):
    server = Server.objects.get(id=serverId)
    channel = server.channels.get(id=channelId)
    msgObject = channel.messages.get(id=messageId, author=user)
    msgObject.delete()
    messageObject = {
        "type": "send_message",
        "option": "delete_message",
        "messageId": messageId,
        "channelId": channelId,
        "serverId": serverId
    }
    return messageObject


@database_sync_to_async
def is_user_in_server(user, serverId):
    server = Server.objects.get(id=int(serverId))
    return user in server.users.all()


@database_sync_to_async
def createNewMessage(user, message, serverId, channelId):
    serverId = int(serverId)
    server = Server.objects.get(id=serverId)
    if user in server.users.all():
        timestamp_limit = timezone.now() - timedelta(
            seconds=config.MESSAGE_DELAY)
        recent_message_count = Message.objects.filter(
            author=user, timestamp__gte=timestamp_limit).count()
        if recent_message_count >= config.MESSAGE_LIMIT:
            return {
                "type":
                "send_message",
                "option":
                "error",
                "userId":
                user.id,
                "message":
                "You have sent too many messages recently. Please wait a few seconds before sending another message."
            }
        channel = Channel.objects.get(id=int(channelId))
        if channel.default_perm_write == False and not user.id == server.owner.id:
            return {
                "type":
                "send_message",
                "option":
                "error",
                "userId":
                user.id,
                "message":
                "You do not have permission to send messages in this channel."
            }
        messageObject = Message.objects.create(content=message, author=user)
        channel.messages.add(messageObject)
        all_urls = re.findall(r'(https?://\S+)', message)
        message_content = mark_safe(
            escape(
                emoji.emojize(message, language="alias",
                              variant="emoji_type"))).replace("\\n",
                                                              "<br>").replace(
                                                                  "\n", "<br>")
        message_content = re.sub(
            "(https?://(?:www\.)?" + config.WEBSITE + "/\S*|https?://\S+)",
            replace_url, message_content)
        return {
            "type":
            "send_message",
            "option":
            "send_message",
            "messageId":
            messageObject.id,
            "message_content":
            message_content,
            "plain_message_content":
            messageObject.content,
            "authorName":
            messageObject.author.username,
            "authorId":
            messageObject.author.id,
            "serverId":
            serverId,
            "channelId":
            channelId,
            "timestamp":
            str(messageObject.timestamp),
            "serverName":
            server.name,
            "channelName":
            channel.name,
            "attachments": [
                "https://" + config.WEBSITE + "/cdn/resize/?url=" + url
                for url in all_urls if is_valid_url(url)
            ]
        }
