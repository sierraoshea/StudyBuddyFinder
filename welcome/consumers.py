import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import UserToUserChat, Message
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = "chat_%s" % self.room_name
        self.user = self.scope['user']

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.user.is_authenticated:
            return
        
        room = await database_sync_to_async(UserToUserChat.objects.get)(roomName=self.room_name)

        m = Message(
            content = message,
            user = self.user, 
            room=room
        )

        await database_sync_to_async(m.save)()

        await self.channel_layer.group_send(
        self.room_group_name, {'type': 'chat_message', 'user': self.user.username, 'message': message}
        )

    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        await self.send(text_data=json.dumps({'message': message, 'user': user}))
