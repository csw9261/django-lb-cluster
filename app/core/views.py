import socket
from django.http import JsonResponse
from django.shortcuts import render

def hello(request):
    return JsonResponse({
        "message": "Hello from Django Cluster",
        "hostname": socket.gethostname()
    })

def index(request):
    return render(request, 'core/index.html', {
        'hostname': socket.gethostname()
    })