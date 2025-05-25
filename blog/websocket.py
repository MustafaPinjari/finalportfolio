import json
import asyncio
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import PageView, UserActivity

class AnalyticsConsumer(AsyncWebsocketConsumer):
    connected_clients = set()
    
    async def connect(self):
        # Add client to connected clients set
        AnalyticsConsumer.connected_clients.add(self)
        
        # Accept the connection
        await self.accept()
        
        # Send initial data
        await self.send_visitor_data()
        
        # Start background task to periodically send updates
        asyncio.create_task(self.send_periodic_updates())
    
    async def disconnect(self, close_code):
        # Remove client from connected clients set
        AnalyticsConsumer.connected_clients.remove(self)
    
    async def receive(self, text_data):
        # Handle incoming messages (if needed)
        data = json.loads(text_data)
        if data.get('type') == 'request_update':
            await self.send_visitor_data()
    
    async def send_visitor_data(self):
        # Get current online visitors (simplified example - in production would use Redis or similar)
        online_count = len(AnalyticsConsumer.connected_clients)
        
        # Get hourly visitor data for the last 24 hours
        last_day = timezone.now() - timedelta(days=1)
        
        # This would normally be done asynchronously using database_sync_to_async
        # But for this example we'll assume it's already in async form
        hourly_data = await self.get_hourly_data(last_day)
        
        await self.send(text_data=json.dumps({
            'type': 'visitor_update',
            'online_count': online_count,
            'hourly_data': hourly_data,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def get_hourly_data(self, last_day):
        # In a real implementation, this would be done with database_sync_to_async
        # For this demo, we'll generate placeholder data
        hours = list(range(24))
        data = []
        
        for hour in hours:
            # Generate some random data for demonstration
            value = 5 + (hour % 12) * 2  # Just a pattern for demo
            data.append({
                'hour': hour,
                'visitors': value
            })
        
        return data
    
    async def send_periodic_updates(self):
        # Send updates every 10 seconds
        while True:
            await asyncio.sleep(10)
            if self in AnalyticsConsumer.connected_clients:
                await self.send_visitor_data()

# Modify this consumer to broadcast to all connected clients
def broadcast_visitor_update():
    """Utility function to broadcast visitor updates to all connected clients"""
    asyncio.create_task(_broadcast_visitor_update())

async def _broadcast_visitor_update():
    online_count = len(AnalyticsConsumer.connected_clients)
    last_day = timezone.now() - timedelta(days=1)
    
    # Get hourly data (placeholder)
    hours = list(range(24))
    hourly_data = []
    for hour in hours:
        value = 5 + (hour % 12) * 2  # Just a pattern for demo
        hourly_data.append({
            'hour': hour,
            'visitors': value
        })
    
    # Broadcast to all connected clients
    for client in AnalyticsConsumer.connected_clients:
        await client.send(text_data=json.dumps({
            'type': 'visitor_update',
            'online_count': online_count,
            'hourly_data': hourly_data,
            'timestamp': timezone.now().isoformat()
        }))
