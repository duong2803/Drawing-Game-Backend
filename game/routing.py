from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/drawing/room/<room_code>/<player_name>',
         consumers.RoomConsumer.as_asgi())
]
