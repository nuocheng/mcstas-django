# ！/usr/bin/python3
# -*- coding: utf-8 -*-
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import user_app.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            user_app.routing.websocket_urlpatterns
        )
    ),
})