import socket
from django.http import JsonResponse

def hello(request):
    return JsonResponse({
        "message": "Hello from Django Cluster",
        "hostname": socket.gethostname()
    })