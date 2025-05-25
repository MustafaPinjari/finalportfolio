import os
import time
import json
import shutil
import tempfile
import zipfile
import subprocess
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.db import connection
from django.core.management import call_command
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import BackupFile, RestorePoint

def ensure_backup_directory():
    """Ensure that the backup directory exists"""
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    return settings.BACKUP_DIR

def create_backup(backup_instance, include_media=True, include_static=False):
    """Create a backup of the database and optionally media files"""
    try:
        # Update status
        backup_instance.status = 'in_progress'
        backup_instance.save()
        
        # Broadcast status update
        broadcast_backup_status(backup_instance)
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Back up database
        db_file = os.path.join(temp_dir, 'db_backup.json')
        with open(db_file, 'w') as f:
            call_command('dumpdata', exclude=['contenttypes', 'auth.permission'], indent=4, stdout=f)
        
        # Create zip file
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        # If the filename doesn't already have a timestamp, add one
        if not backup_instance.filename or not backup_instance.filename.endswith('.zip'):
            backup_instance.filename = f"backup_{timestamp}.zip"
            backup_instance.save()
            
        zip_path = os.path.join(ensure_backup_directory(), backup_instance.filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add database dump
            zipf.write(db_file, 'db_backup.json')
            
            # Add media files if requested
            if include_media and os.path.exists(settings.MEDIA_ROOT):
                for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.join('media', os.path.relpath(filepath, settings.MEDIA_ROOT))
                        zipf.write(filepath, arcname)
                        
                        # Periodically update progress
                        broadcast_backup_progress(backup_instance, 'Adding media files')
            
            # Add static files if requested
            if include_static and os.path.exists(settings.STATIC_ROOT):
                for root, dirs, files in os.walk(settings.STATIC_ROOT):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.join('static', os.path.relpath(filepath, settings.STATIC_ROOT))
                        zipf.write(filepath, arcname)
                        
                        # Periodically update progress
                        broadcast_backup_progress(backup_instance, 'Adding static files')
            
            # Add backup metadata
            import django
            metadata = {
                'timestamp': timestamp,
                'django_version': django.__version__,
                'include_media': include_media,
                'include_static': include_static,
                'backup_id': str(backup_instance.id)
            }
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as meta_file:
                json.dump(metadata, meta_file)
                meta_file_path = meta_file.name
            
            zipf.write(meta_file_path, 'backup_metadata.json')
            os.unlink(meta_file_path)
        
        # Update backup record
        # No need to update filename as it was already set earlier
        backup_instance.size = os.path.getsize(zip_path)
        backup_instance.status = 'completed'
        backup_instance.completed_at = timezone.now()
        backup_instance.save()
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        # Broadcast completion
        broadcast_backup_status(backup_instance)
        
        return True, zip_path
    
    except Exception as e:
        # Update backup record with error
        backup_instance.status = 'failed'
        backup_instance.note = f"Error: {str(e)}"
        backup_instance.save()
        
        # Broadcast error
        broadcast_backup_status(backup_instance)
        
        # Clean up
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)
        
        return False, str(e)

def restore_backup(restore_point):
    """Restore a backup from a restore point"""
    try:
        # Update status
        restore_point.status = 'in_progress'
        restore_point.save()
        
        # Broadcast status update
        broadcast_restore_status(restore_point)
        
        # Get backup file
        backup_file = restore_point.backup_file
        backup_path = backup_file.get_file_path()
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Extract backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Check metadata
        metadata_path = os.path.join(temp_dir, 'backup_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        # Restore database
        db_backup = os.path.join(temp_dir, 'db_backup.json')
        if os.path.exists(db_backup):
            # Clear database tables (except critical ones)
            with connection.cursor() as cursor:
                tables = connection.introspection.table_names()
                for table in tables:
                    if table not in ['auth_user', 'django_migrations', 'django_content_type', 'auth_permission']:
                        cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE;')
            
            # Load data from backup
            call_command('loaddata', db_backup)
            
            # Broadcast progress update
            broadcast_restore_progress(restore_point, 'Database restored')
        
        # Restore media files if they exist in the backup
        media_dir = os.path.join(temp_dir, 'media')
        if os.path.exists(media_dir) and metadata.get('include_media', False):
            # Clear existing media
            if os.path.exists(settings.MEDIA_ROOT):
                for item in os.listdir(settings.MEDIA_ROOT):
                    item_path = os.path.join(settings.MEDIA_ROOT, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.unlink(item_path)
            
            # Copy media files from backup
            for item in os.listdir(media_dir):
                src = os.path.join(media_dir, item)
                dst = os.path.join(settings.MEDIA_ROOT, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            
            # Broadcast progress update
            broadcast_restore_progress(restore_point, 'Media files restored')
        
        # Restore static files if they exist in the backup
        static_dir = os.path.join(temp_dir, 'static')
        if os.path.exists(static_dir) and metadata.get('include_static', False):
            # Clear existing static files
            if os.path.exists(settings.STATIC_ROOT):
                for item in os.listdir(settings.STATIC_ROOT):
                    item_path = os.path.join(settings.STATIC_ROOT, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.unlink(item_path)
            
            # Copy static files from backup
            for item in os.listdir(static_dir):
                src = os.path.join(static_dir, item)
                dst = os.path.join(settings.STATIC_ROOT, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            
            # Broadcast progress update
            broadcast_restore_progress(restore_point, 'Static files restored')
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        # Update restore point record
        restore_point.status = 'completed'
        restore_point.restored_at = timezone.now()
        restore_point.save()
        
        # Broadcast completion
        broadcast_restore_status(restore_point)
        
        return True, "Restore completed successfully"
    
    except Exception as e:
        # Update restore point record with error
        restore_point.status = 'failed'
        restore_point.error_message = str(e)
        restore_point.save()
        
        # Broadcast error
        broadcast_restore_status(restore_point)
        
        # Clean up
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)
        
        return False, str(e)

def import_backup(uploaded_file, name, note=None):
    """Import a backup file uploaded by user"""
    try:
        # Create a new backup record
        backup = BackupFile(
            filename=uploaded_file.name,
            backup_type='manual',
            status='in_progress',
            note=note
        )
        backup.save()
        
        # Broadcast status update
        broadcast_backup_status(backup)
        
        # Save the uploaded file to the backup directory
        ensure_backup_directory()
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"import_{timestamp}_{uploaded_file.name}"
        filepath = os.path.join(settings.BACKUP_DIR, filename)
        
        with open(filepath, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Update backup record
        backup.filename = filename
        backup.size = os.path.getsize(filepath)
        backup.status = 'completed'
        backup.completed_at = timezone.now()
        backup.save()
        
        # Broadcast completion
        broadcast_backup_status(backup)
        
        return True, backup
    
    except Exception as e:
        if 'backup' in locals():
            backup.status = 'failed'
            backup.note = f"Error: {str(e)}"
            backup.save()
            
            # Broadcast error
            broadcast_backup_status(backup)
        
        return False, str(e)

def cleanup_old_backups(schedule):
    """Delete old backups based on retention policy"""
    backups = BackupFile.objects.filter(
        schedule=schedule,
        status='completed',
        is_deleted=False
    ).order_by('-created_at')
    
    # Keep only the newest N backups
    if backups.count() > schedule.retention_count:
        for backup in backups[schedule.retention_count:]:
            backup.delete_file()

# Realtime notifications via WebSockets
def broadcast_backup_status(backup):
    """Broadcast backup status update to WebSocket clients"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'backup_updates',
        {
            'type': 'backup_status',
            'id': str(backup.id),
            'status': backup.status,
            'filename': backup.filename,
            'created_at': backup.created_at.isoformat(),
            'completed_at': backup.completed_at.isoformat() if backup.completed_at else None,
            'size': backup.size,
            'note': backup.note
        }
    )

def broadcast_backup_progress(backup, message):
    """Broadcast backup progress update to WebSocket clients"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'backup_updates',
        {
            'type': 'backup_progress',
            'id': str(backup.id),
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
    )

def broadcast_restore_status(restore_point):
    """Broadcast restore status update to WebSocket clients"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'backup_updates',
        {
            'type': 'restore_status',
            'id': str(restore_point.id),
            'name': restore_point.name,
            'status': restore_point.status,
            'created_at': restore_point.created_at.isoformat(),
            'restored_at': restore_point.restored_at.isoformat() if restore_point.restored_at else None,
            'error_message': restore_point.error_message
        }
    )

def broadcast_restore_progress(restore_point, message):
    """Broadcast restore progress update to WebSocket clients"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'backup_updates',
        {
            'type': 'restore_progress',
            'id': str(restore_point.id),
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
    )
