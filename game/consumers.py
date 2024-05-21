import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room, Player


class RoomConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_code']
        self.player_name = self.scope['url_route']['kwargs']['player_name']
        self.room_group_name = f'room_{self.room_id}'

        room: Room
        created: bool

        room, created = Room.objects.get_or_create(id=self.room_id)
        current_user_count = room.players.count()

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        player: Player = Player.objects.create(
            name=self.player_name, room_id=room)
        self.player_id = player.id

        self.send(json.dumps({
            'type': 'player_id',
            'payload': {
                'player_id': json.dumps(self.player_id)
            }
        }))

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'player_join',
                'player_name': self.player_name
            }
        )

    def player_join(self, event):
        player_name = event['player_name']
        players_list: list[Player] = Player.objects.filter(
            room_id=self.room_id)

        ready_list: list[bool] = [player.ready for player in players_list]
        players_list: list[str] = [player.name for player in players_list]

        self.send(text_data=json.dumps({
            'type': 'player_join',
            'payload': {
                'player_name': player_name,
                'players_list': json.dumps(players_list),
                'ready_list': json.dumps(ready_list)
            }
        }))

    def receive(self, text_data=None, bytes_data=None):
        json_data: dict = json.loads(text_data)
        data_type = json_data.get('type')

        if data_type == 'ready':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'player_ready',
                    'player_id': self.player_id
                }
            )

        elif data_type == 'ready_cancel':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'player_ready_cancel',
                    'player_id': self.player_id
                }
            )

        return super().receive(text_data, bytes_data)

    def player_ready(self, event):
        player_id = event['player_id']
        player = Player.objects.get(id=player_id)
        player.ready = True
        player.save()

        players_list: list[Player] = Player.objects.filter(
            room_id=self.room_id)

        ready_list: list[bool] = [player.ready for player in players_list]

        self.send(text_data=json.dumps({
            'type': 'ready',
            'payload': {
                'ready_list': json.dumps(ready_list)
            }
        }))

        start_game: bool = True
        for ready in ready_list:
            start_game &= ready

        if start_game:
            self.send(text_data=json.dumps({
                'type': 'start_game',
                'payload': {

                }
            }))

    def player_ready_cancel(self, event):
        player_id = event['player_id']
        player = Player.objects.get(id=player_id)
        player.ready = False
        player.save()

        players_list: list[Player] = Player.objects.filter(
            room_id=self.room_id)

        ready_list: list[bool] = [player.ready for player in players_list]

        self.send(text_data=json.dumps({
            'type': 'ready_cancel',
            'payload': {
                'ready_list': json.dumps(ready_list)
            }
        }))

    def disconnect(self, code):
        try:
            player = Player.objects.get(
                id=self.player_id)
            player.delete()

            room_players_count = Player.objects.filter(
                room_id=self.room_id).count()
            if room_players_count == 0:
                Room.objects.filter(id=self.room_id).delete()
                print(f'Deleted room {self.room_id}!!')

        except Player.DoesNotExist:
            pass

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'player_exit',
                'player_name': self.player_name
            }
        )

    def player_exit(self, event):
        player_name = event['player_name']
        players_list: list[Player] = Player.objects.filter(
            room_id=self.room_id)

        ready_list: list[bool] = [player.ready for player in players_list]
        players_list: list[str] = [player.name for player in players_list]

        self.send(json.dumps({
            'type': 'player_exit',
            'payload': {
                'player_name': player_name,
                'players_list': json.dumps(players_list),
                'ready_list': json.dumps(ready_list)
            }
        }))


class GameConsumer(WebsocketConsumer):
    def connect(self):
        pass

    def receive(self, text_data=None, bytes_data=None):
        pass

    def disconnect(self, code):
        pass
