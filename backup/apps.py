from django.apps import AppConfig


class BackupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backup'
    
    def ready(self):
        """Initialize any app-specific tasks when Django starts"""
        # Import signals and any other initialization code
        try:
            # Setup periodic tasks if scheduler is available
            from django.conf import settings
            import os
            
            # Create backup directory if it doesn't exist
            backup_dir = getattr(settings, 'BACKUP_DIR', os.path.join(settings.BASE_DIR, 'backups'))
            os.makedirs(backup_dir, exist_ok=True)
            
        except ImportError:
            # Handle the case when this is called during migrations
            pass
