import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Room, Player, Question, Result
import random
from . import doodle_model
import numpy as np
from django.utils import timezone
from threading import Timer
from time import sleep


labels = ['bear', 'bee', 'bird', 'cat', 'dog', 'dolphin', 'elephant', 'frog',
          'giraffe', 'lion', 'monkey', 'octopus', 'panda', 'penguin', 'pig', 'rabbit', 'shark',
          'snake', 'tiger', 'zebra', 'apple', 'banana', 'bread', 'broccoli', 'carrot', 'hamburger',
          'hot dog', 'ice cream', 'lollipop', 'mushroom', 'onion', 'pear', 'pineapple', 'pizza',
          'watermelon', 'alarm clock', 'backpack', 'bed', 'ceiling fan', 'chair', 'clock', 'coffee cup',
          'computer', 'couch', 'dishwasher', 'door', 'dresser', 'knife', 'ladder', 'light bulb', 'oven',
          'table', 'teapot', 'television', 'toilet', 'ambulance', 'bicycle', 'bulldozer', 'bus', 'car', 'motorbike',
          'parachute', 'police car', 'sailboat', 'school bus', 'skateboard', 'speedboat', 'tractor', 'train', 'truck']

model = doodle_model.DoodleModel()


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_code']
        self.player_name = self.scope['url_route']['kwargs']['player_name']
        self.room_group_name = f'room_{self.room_id}'

        self.game_duration = 60
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

        elif data_type == 'submit':
            grid = json_data.get('grid')
            grid = json.loads(grid)
            ngrid = [[0 for _ in range(28)] for _ in range(28)]
            for i in range(28):
                for j in range(28):
                    ngrid[i][j] = grid[i * 28 + j]
            ngrid = np.array(ngrid)

            label = json_data.get('label')
            label = json.loads(label)

            self.submit(ngrid, label)

        return super().receive(text_data, bytes_data)

    def player_ready(self, event):
        player_id = event['player_id']
        player = Player.objects.get(id=player_id)
        player_name = player.name
        player.ready = True
        player.save()

        players_list: list[Player] = Player.objects.filter(
            room_id=self.room_id)

        ready_list: list[bool] = [player.ready for player in players_list]

        self.send(text_data=json.dumps({
            'type': 'ready',
            'payload': {
                'player_name': json.dumps(player_name),
                'ready_list': json.dumps(ready_list)
            }
        }))

        start_game: bool = True
        for ready in ready_list:
            start_game &= ready

        if start_game:
            question_count = Question.objects.filter(
                room_id=self.room_id).count()

            print(f'question_count: {question_count}')
            if question_count == 0:
                questions = random.sample(labels, 5)
                room = Room.objects.get(id=self.room_id)
                for question in questions:
                    Question.objects.create(label=question, room_id=room)

            questions = Question.objects.filter(room_id=self.room_id)
            questions = [question.label for question in questions]
            self.send(text_data=json.dumps({
                'type': 'start_game',
                'payload': {
                    'questions': json.dumps(questions)
                }
            }))

            self.question_solved = [False for _ in range(5)]
            self.question_penalty = [0 for _ in range(5)]

            current_player = Player.objects.get(id=self.player_id)
            Result.objects.create(player_id=current_player)

            current_room = Room.objects.get(id=self.room_id)
            if current_room.start_time is None:
                current_room.start_time = timezone.now()
                current_room.save()

            self.timer = Timer((current_room.start_time + timezone.timedelta(
                seconds=self.game_duration) - timezone.now()).total_seconds(), self.game_end)
            self.timer.start()

    def player_ready_cancel(self, event):
        player_id = event['player_id']
        player = Player.objects.get(id=player_id)
        player.ready = False
        player.save()

        player_name = player.name

        players_list: list[Player] = Player.objects.filter(
            room_id=self.room_id)

        ready_list: list[bool] = [player.ready for player in players_list]

        self.send(text_data=json.dumps({
            'type': 'ready_cancel',
            'payload': {
                'player_name': json.dumps(player_name),
                'ready_list': json.dumps(ready_list)
            }
        }))

    def submit(self, grid, label):
        prediction = model.top3_predict(grid)
        labels_list = Question.objects.filter(room_id=self.room_id)
        labels_list: list[str] = [l.label for l in labels_list]

        label_index = labels_list.index(label)

        if label in prediction[0]:
            verdict = 'Accepted'
            if self.question_solved[label_index] == False:
                self.question_solved[label_index] = True
                player_result = Result.objects.filter(player_id=self.player_id)
                assert (len(player_result) == 1)
                result_id = player_result.first().id
                player_result = Result.objects.get(id=result_id)
                player_result.solved += 1

                start_time = Room.objects.get(id=self.room_id).start_time
                solved_time = int(
                    (timezone.now() - start_time).total_seconds())

                print(f'Solved time: {solved_time}')
                print(f'Penalty: {self.question_penalty[label_index]}')

                player_result.penalty += self.question_penalty[label_index] * \
                    5 + solved_time

                player_result.save()

        else:
            verdict = 'Wrong answer'
            if self.question_solved[label_index] == False:
                self.question_penalty[label_index] += 1

        self.send(json.dumps({
            'type': 'verdict',
            'payload': {
                'verdict': json.dumps(verdict)
            }
        }))

    def game_end(self):
        self.send(json.dumps({
            'type': 'game_end'
        }))

        result_data = []
        results = Result.objects.filter(player_id__room_id=self.room_id)
        for result in results:
            player = result.player_id
            result_data.append({
                'name': player.name,
                'solved': result.solved,
                'penalty': result.penalty
            })

        self.send(json.dumps({
            'type': 'scoreboard',
            'payload': {
                'scoreboard': json.dumps(result_data)
            }
        }))

        results.delete()
        room = Room(id=self.room_id)
        room.start_time = None

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

        print(f'Player {self.player_name} has exited')
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

        print(f'Player {player_name} has exited')

        ready_list: list[bool] = [player.ready for player in players_list]
        players_list: list[str] = [player.name for player in players_list]

        self.send(json.dumps({
            'type': 'player_exit',
            'payload': {
                'player_name': json.dumps(player_name),
                'players_list': json.dumps(players_list),
                'ready_list': json.dumps(ready_list)
            }
        }))
