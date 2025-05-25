import os
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings

class BackupSchedule(models.Model):
    """Model to store backup schedule settings"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='weekly')
    day_of_week = models.IntegerField(null=True, blank=True, help_text='Day of week (0-6, where 0 is Monday)')
    day_of_month = models.IntegerField(null=True, blank=True, help_text='Day of month (1-31)')
    time = models.TimeField(default=timezone.now)
    retention_count = models.IntegerField(default=5, help_text='Number of backups to keep')
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"

class BackupFile(models.Model):
    """Model to store backup file information"""
    TYPE_CHOICES = [
        ('auto', 'Automated'),
        ('manual', 'Manual'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    backup_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='manual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    size = models.BigIntegerField(default=0)
    schedule = models.ForeignKey(BackupSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def get_file_path(self):
        """Return the absolute path to the backup file"""
        return os.path.join(settings.BACKUP_DIR, self.filename)
    
    def file_exists(self):
        """Check if the backup file exists on disk"""
        return os.path.exists(self.get_file_path())
    
    def delete_file(self):
        """Delete the actual backup file from disk"""
        if self.file_exists():
            os.remove(self.get_file_path())
            self.is_deleted = True
            self.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.filename} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class RestorePoint(models.Model):
    """Model to store restore points"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    backup_file = models.ForeignKey(BackupFile, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    restored_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
