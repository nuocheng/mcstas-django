from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.urls import path
from user_app import consumers
websocket_urlpatterns = [
    path("/",consumers.ChatConsumer.as_asgi())
]