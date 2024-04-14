from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/drawing/game/<room_code>', consumers.GameConsumer.as_asgi())
]
