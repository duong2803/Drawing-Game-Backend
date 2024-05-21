from django.db import models

class Room(models.Model):
    id = models.AutoField(primary_key=True)
    
    def __str__(self):
        return f"Room {self.id}"

class Player(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    ready = models.BooleanField(default=False)

    def __str__(self):
        return f"Player {self.id} ({self.name}) in Room {self.room_id}"