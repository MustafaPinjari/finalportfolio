import os
import logging
from datetime import datetime
from django.utils import timezone
from django.conf import settings

from .models import BackupSchedule, BackupFile
from .utils import create_backup, cleanup_old_backups

logger = logging.getLogger(__name__)

def check_backup_schedules():
    """Check if any backups need to be run according to schedule"""
    now = timezone.now()
    today = now.date()
    current_time = now.time()
    backups_run = 0
    
    # Get all enabled schedules
    schedules = BackupSchedule.objects.filter(enabled=True)
    
    for schedule in schedules:
        should_run = False
        
        # Check if it's time to run based on frequency
        if schedule.frequency == 'daily':
            # Run daily at the specified time
            should_run = current_time.hour == schedule.time.hour and \
                        current_time.minute >= schedule.time.minute and \
                        current_time.minute < schedule.time.minute + 5  # Run within 5 minutes of scheduled time
        
        elif schedule.frequency == 'weekly' and schedule.day_of_week is not None:
            # Run weekly on the specified day at the specified time
            if today.weekday() == schedule.day_of_week:
                should_run = current_time.hour == schedule.time.hour and \
                            current_time.minute >= schedule.time.minute and \
                            current_time.minute < schedule.time.minute + 5
        
        elif schedule.frequency == 'monthly' and schedule.day_of_month is not None:
            # Run monthly on the specified day at the specified time
            if today.day == schedule.day_of_month:
                should_run = current_time.hour == schedule.time.hour and \
                            current_time.minute >= schedule.time.minute and \
                            current_time.minute < schedule.time.minute + 5
        
        if should_run:
            logger.info(f"Running scheduled backup: {schedule.name}")
            
            # Create backup record
            backup = BackupFile(
                filename=f"scheduled_{schedule.name.lower().replace(' ', '_')}_{now.strftime('%Y%m%d_%H%M%S')}.zip",
                backup_type='auto',
                schedule=schedule,
                note=f"Automated backup from schedule: {schedule.name}"
            )
            backup.save()
            
            # Run the backup
            try:
                success, result = create_backup(backup, include_media=True)
                if success:
                    logger.info(f"Scheduled backup completed: {backup.filename}")
                    backups_run += 1
                    
                    # Cleanup old backups
                    cleanup_old_backups(schedule)
                else:
                    logger.error(f"Scheduled backup failed: {result}")
            except Exception as e:
                logger.exception(f"Error during scheduled backup: {str(e)}")
                backup.status = 'failed'
                backup.note = f"Error: {str(e)}"
                backup.save()
    
    return backups_run
