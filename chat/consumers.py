import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message
from django.contrib.auth import get_user_model
from django.utils import timezone
import pytz

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        chat = await self.get_chat()
        message_obj = await self.save_message(self.user.id, message, chat.id)
        
        ist_time = message_obj.timestamp.astimezone(pytz.timezone('Asia/Kolkata'))
        print(f"Message sent: {message} at {ist_time.strftime('%Y-%m-%d %H:%M:%S')} IST")
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': self.user.id,
                'username': self.user.get_full_name() or self.user.username,
                'timestamp': ist_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )
        
        # Send update to all users
        await self.update_chat_list(chat, message_obj)

    async def chat_message(self, event):
        ist_time = pytz.timezone('Asia/Kolkata').localize(timezone.datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S'))
        print(f"Message received: {event['message']} at {ist_time.strftime('%Y-%m-%d %H:%M:%S')} IST")
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            **event
        }))

    @database_sync_to_async
    def save_message(self, user_id, content, chat_id):
        user = User.objects.get(id=user_id)
        chat = Chat.objects.get(id=chat_id)
        ist_now = timezone.now().astimezone(pytz.timezone('Asia/Kolkata'))
        message = Message.objects.create(chat=chat, sender=user, content=content, timestamp=ist_now)
        chat.last_message_time = message.timestamp
        chat.save()
        return message

    @database_sync_to_async
    def get_chat(self):
        return Chat.objects.get(id=self.room_name)

    async def update_chat_list(self, chat, message):
        ist_time = message.timestamp.astimezone(pytz.timezone('Asia/Kolkata'))
        update_data = {
            'type': 'chat_list_update',
            'chat_id': str(chat.id),
            'last_message': message.content,
            'last_message_time': ist_time.strftime('%Y-%m-%d %H:%M:%S'),
            'sender_name': message.sender.get_full_name() or message.sender.username,
        }
        
        # Send update to all users
        await self.channel_layer.group_send('global', update_data)

    async def chat_list_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update_chat_list',
            **event
        }))

    @database_sync_to_async
    def get_chat_participants(self, chat):
        return list(chat.participants.all())

class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}'

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            'global',
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            'global',
            self.channel_name
        )

    async def chat_list_update(self, event):
        await self.send(text_data=json.dumps(event))