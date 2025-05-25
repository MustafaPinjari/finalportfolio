from django.urls import path
from blog.websocket import AnalyticsConsumer
from backup.consumers import BackupConsumer

# Define WebSocket URL patterns
websocket_urlpatterns = [
    path('ws/analytics/', AnalyticsConsumer.as_asgi()),
    path('ws/backup/', BackupConsumer.as_asgi()),
]
