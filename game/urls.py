from django.urls import path
from . import views

urlpatterns = [
    path('game/', views.start_game, name='game'),
    path('get-levels/', views.get_levels, name='get-levels'),
    path('get-prediction/', views.get_prediction, name='get-prediction'),
]