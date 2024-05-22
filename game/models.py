from django.db import models


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    start_time = models.DateTimeField(null=True)

    def __str__(self):
        return f"Room {self.id}."


class Player(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    room_id = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='players')
    ready = models.BooleanField(default=False)

    def __str__(self):
        return f"Player {self.id} ({self.name}) in Room {self.room_id}."


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=255)
    room_id = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='rooms')

    def __str__(self):
        return f'Question id {self.id} with label {self.label} in the room {self.room_id}.'


class Result(models.Model):
    id = models.AutoField(primary_key=True)
    player_id = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='players')
    solved = models.IntegerField(default=0)
    penalty = models.IntegerField(default=0)

    def __str__(self):
        return f'Player with id {self.player_id} has solved {self.solved} with penalty {self.penalty}.'
