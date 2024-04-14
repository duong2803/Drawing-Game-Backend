import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_name}'
        print(self.room_group_name)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, 
            {
                'type': 'run_game',
                'payload': text_data
            }
        )
        return super().receive(text_data, bytes_data)

    def run_game(self, event):
        data = event['payload']

        self.send(text_data=data)

    def disconnect(self, code):

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
