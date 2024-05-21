from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
import random
from . import doodle_model
import json


labels = ['bear', 'bee', 'bird', 'cat', 'dog', 'dolphin', 'elephant', 'frog',
          'giraffe', 'lion', 'monkey', 'octopus', 'panda', 'penguin', 'pig', 'rabbit', 'shark',
          'snake', 'tiger', 'zebra', 'apple', 'banana', 'bread', 'broccoli', 'carrot', 'hamburger',
          'hot dog', 'ice cream', 'lollipop', 'mushroom', 'onion', 'pear', 'pineapple', 'pizza',
          'watermelon', 'alarm clock', 'backpack', 'bed', 'ceiling fan', 'chair', 'clock', 'coffee cup',
          'computer', 'couch', 'dishwasher', 'door', 'dresser', 'knife', 'ladder', 'light bulb', 'oven',
          'table', 'teapot', 'television', 'toilet', 'ambulance', 'bicycle', 'bulldozer', 'bus', 'car', 'motorbike',
          'parachute', 'police car', 'sailboat', 'school bus', 'skateboard', 'speedboat', 'tractor', 'train', 'truck']

model = doodle_model.DoodleModel()


def start_game(request: HttpRequest) -> JsonResponse:
    return JsonResponse({'data': 'Hello'}, status=200)


@csrf_exempt
def create_level(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try:
            data: dict = json.loads(request.body.decode('utf-8'))
            levels: list[str] = data.get('levels')
            
            return JsonResponse({
                'message': 'OK',
            }, status=200)
        except:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
    return JsonResponse({'message': 'OK'}, status=200)


def get_levels(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        try:
            # data: dict = json.loads(request.body.decode('utf-8'))
            quantity: int = int(request.GET['quantity'])
            print(f'quantity: {quantity}')
            levels: list[str] = random.sample(labels, quantity)
            return JsonResponse({
                'message': 'OK',
                'levels': levels
            }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'message': 'OK'}, status=200)


@csrf_exempt
def get_prediction(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try:
            data: dict = json.loads(request.body.decode('utf-8'))
            grid: list = data.get('grid')
            model.set_data(grid)

            top3_predict = model.top3_predict()
            print(top3_predict)
            return JsonResponse({
                'message': 'OK',
                'prediction': top3_predict[0],
                'probability': top3_predict[1],
            }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
    return JsonResponse({
        'message': 'OK'
    }, status=200)
