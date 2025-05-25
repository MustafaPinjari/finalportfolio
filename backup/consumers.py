import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class BackupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated and has admin privileges
        if self.scope['user'].is_anonymous or not self.scope['user'].is_staff:
            await self.close()
            return
            
        # Add to backup_updates group
        await self.channel_layer.group_add(
            'backup_updates',
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send initial status message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to backup updates'
        }))
    
    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            'backup_updates',
            self.channel_name
        )
    
    # Receive message from WebSocket (from client)
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        # Handle different types of messages
        if message_type == 'request_status':
            # Client requesting current status
            await self.send_status_update()
    
    # Handlers for messages from the group
    async def backup_status(self, event):
        # Send backup status update to WebSocket
        await self.send(text_data=json.dumps(event))
    
    async def backup_progress(self, event):
        # Send backup progress update to WebSocket
        await self.send(text_data=json.dumps(event))
    
    async def restore_status(self, event):
        # Send restore status update to WebSocket
        await self.send(text_data=json.dumps(event))
    
    async def restore_progress(self, event):
        # Send restore progress update to WebSocket
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def send_status_update(self):
        # This could query current backup/restore status and send it
        # Implementation will depend on what status info you want to provide
        pass
