from django.urls import re_path,path

from user_app import consumers

websocket_urlpatterns = [
    # 前端请求websocket连接
    # path('ws/result/', consumers.SyncConsumer),
]