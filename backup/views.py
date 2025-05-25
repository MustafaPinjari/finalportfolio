import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import BackupSchedule, BackupFile, RestorePoint
from .forms import BackupScheduleForm, ManualBackupForm, RestoreForm, ImportForm
from .utils import (
    create_backup, restore_backup, import_backup, cleanup_old_backups,
    broadcast_backup_status, broadcast_restore_status
)

# Helper function to check if user is admin or staff
def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_backup_dashboard(request):
    """Main backup and restore dashboard"""
    # Get recent backups
    recent_backups = BackupFile.objects.filter(is_deleted=False).order_by('-created_at')[:5]
    
    # Get schedules
    schedules = BackupSchedule.objects.all().order_by('-created_at')
    
    # Get restore points
    restore_points = RestorePoint.objects.all().order_by('-created_at')[:5]
    
    # Get stats
    total_backups = BackupFile.objects.filter(is_deleted=False).count()
    successful_backups = BackupFile.objects.filter(status='completed', is_deleted=False).count()
    total_size = sum(b.size for b in BackupFile.objects.filter(is_deleted=False))
    
    context = {
        'active_tab': 'backup',
        'recent_backups': recent_backups,
        'schedules': schedules,
        'restore_points': restore_points,
        'stats': {
            'total_backups': total_backups,
            'successful_backups': successful_backups,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size else 0,
        }
    }
    
    return render(request, 'admin/admin_backup.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def backup_list(request):
    """List all backups with pagination"""
    backups = BackupFile.objects.filter(is_deleted=False).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(backups, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active_tab': 'backup',
        'page_obj': page_obj,
        'total_backups': backups.count(),
    }
    
    return render(request, 'admin/admin_backup_list.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def backup_detail(request, backup_id):
    """View details of a specific backup"""
    backup = get_object_or_404(BackupFile, id=backup_id)
    
    # Check if file exists on disk
    file_exists = backup.file_exists()
    
    # Get related restore points
    restore_points = RestorePoint.objects.filter(backup_file=backup).order_by('-created_at')
    
    context = {
        'active_tab': 'backup',
        'backup': backup,
        'file_exists': file_exists,
        'restore_points': restore_points,
    }
    
    return render(request, 'admin/admin_backup_detail.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def backup_delete(request, backup_id):
    """Delete a backup"""
    backup = get_object_or_404(BackupFile, id=backup_id)
    
    if request.method == 'POST':
        # Delete the file
        if backup.file_exists():
            backup.delete_file()
        
        # Mark as deleted
        backup.is_deleted = True
        backup.save()
        
        messages.success(request, f'Backup "{backup.filename}" has been deleted.')
        return redirect('backup_list')
    
    context = {
        'active_tab': 'backup',
        'backup': backup,
    }
    
    return render(request, 'admin/admin_backup_delete.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def backup_download(request, backup_id):
    """Download a backup file"""
    backup = get_object_or_404(BackupFile, id=backup_id)
    
    if not backup.file_exists():
        messages.error(request, f'Backup file "{backup.filename}" does not exist.')
        return redirect('backup_detail', backup_id=backup_id)
    
    # Serve the file
    file_path = backup.get_file_path()
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{backup.filename}"'
        return response

@login_required
@user_passes_test(is_admin_or_staff)
def create_manual_backup(request):
    """Create a manual backup"""
    if request.method == 'POST':
        form = ManualBackupForm(request.POST)
        if form.is_valid():
            # Generate timestamp for filename
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            
            # Create backup record
            backup = BackupFile(
                filename=f"manual_backup_{timestamp}.zip",
                backup_type='manual',
                note=form.cleaned_data['note']
            )
            backup.save()
            
            # Create the backup
            success, result = create_backup(
                backup,
                include_media=form.cleaned_data['include_media'],
                include_static=form.cleaned_data['include_static']
            )
            
            if success:
                messages.success(request, 'Backup created successfully.')
            else:
                messages.error(request, f'Error creating backup: {result}')
            
            return redirect('backup_detail', backup_id=backup.id)
    else:
        form = ManualBackupForm()
    
    context = {
        'active_tab': 'backup',
        'form': form,
    }
    
    return render(request, 'admin/admin_backup_create.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def manage_backup_schedules(request):
    """Manage backup schedules"""
    schedules = BackupSchedule.objects.all().order_by('-created_at')
    
    context = {
        'active_tab': 'backup',
        'schedules': schedules,
    }
    
    return render(request, 'admin/admin_backup_schedules.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def create_backup_schedule(request):
    """Create a new backup schedule"""
    if request.method == 'POST':
        form = BackupScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Backup schedule created successfully.')
            return redirect('manage_backup_schedules')
    else:
        form = BackupScheduleForm()
    
    context = {
        'active_tab': 'backup',
        'form': form,
    }
    
    return render(request, 'admin/admin_backup_schedule_create.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def edit_backup_schedule(request, schedule_id):
    """Edit a backup schedule"""
    schedule = get_object_or_404(BackupSchedule, id=schedule_id)
    
    if request.method == 'POST':
        form = BackupScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Backup schedule updated successfully.')
            return redirect('manage_backup_schedules')
    else:
        form = BackupScheduleForm(instance=schedule)
    
    context = {
        'active_tab': 'backup',
        'form': form,
        'schedule': schedule,
    }
    
    return render(request, 'admin/admin_backup_schedule_edit.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def delete_backup_schedule(request, schedule_id):
    """Delete a backup schedule"""
    schedule = get_object_or_404(BackupSchedule, id=schedule_id)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Backup schedule deleted successfully.')
        return redirect('manage_backup_schedules')
    
    context = {
        'active_tab': 'backup',
        'schedule': schedule,
    }
    
    return render(request, 'admin/admin_backup_schedule_delete.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def restore_list(request):
    """List all restore points"""
    restore_points = RestorePoint.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(restore_points, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active_tab': 'backup',
        'page_obj': page_obj,
        'total_restore_points': restore_points.count(),
    }
    
    return render(request, 'admin/admin_restore_list.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def create_restore_point(request):
    """Create a new restore point"""
    if request.method == 'POST':
        form = RestoreForm(request.POST)
        if form.is_valid():
            restore_point = form.save()
            messages.success(request, 'Restore point created successfully.')
            return redirect('restore_detail', restore_id=restore_point.id)
    else:
        form = RestoreForm()
    
    context = {
        'active_tab': 'backup',
        'form': form,
    }
    
    return render(request, 'admin/admin_restore_create.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def restore_detail(request, restore_id):
    """View details of a specific restore point"""
    restore_point = get_object_or_404(RestorePoint, id=restore_id)
    
    context = {
        'active_tab': 'backup',
        'restore_point': restore_point,
    }
    
    return render(request, 'admin/admin_restore_detail.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def execute_restore(request, restore_id):
    """Execute a restore operation"""
    restore_point = get_object_or_404(RestorePoint, id=restore_id)
    
    if request.method == 'POST':
        # Confirm restore
        confirmation = request.POST.get('confirm_restore')
        if confirmation == 'confirm':
            # Execute restore
            success, message = restore_backup(restore_point)
            
            if success:
                messages.success(request, 'Restore completed successfully.')
            else:
                messages.error(request, f'Error during restore: {message}')
            
            return redirect('restore_detail', restore_id=restore_point.id)
        else:
            messages.error(request, 'Restore confirmation failed.')
    
    context = {
        'active_tab': 'backup',
        'restore_point': restore_point,
    }
    
    return render(request, 'admin/admin_restore_execute.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def delete_restore_point(request, restore_id):
    """Delete a restore point"""
    restore_point = get_object_or_404(RestorePoint, id=restore_id)
    
    if request.method == 'POST':
        restore_point.delete()
        messages.success(request, 'Restore point deleted successfully.')
        return redirect('restore_list')
    
    context = {
        'active_tab': 'backup',
        'restore_point': restore_point,
    }
    
    return render(request, 'admin/admin_restore_delete.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def import_backup_view(request):
    """Import a backup file"""
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            success, result = import_backup(
                form.cleaned_data['backup_file'],
                form.cleaned_data['name'],
                form.cleaned_data['note']
            )
            
            if success:
                messages.success(request, 'Backup imported successfully.')
                return redirect('backup_detail', backup_id=result.id)
            else:
                messages.error(request, f'Error importing backup: {result}')
    else:
        form = ImportForm()
    
    context = {
        'active_tab': 'backup',
        'form': form,
    }
    
    return render(request, 'admin/admin_backup_import.html', context)

# API endpoints for AJAX calls
@login_required
@user_passes_test(is_admin_or_staff)
@csrf_exempt
def api_backup_status(request, backup_id):
    """API endpoint to check backup status"""
    try:
        backup = BackupFile.objects.get(id=backup_id)
        data = {
            'id': str(backup.id),
            'status': backup.status,
            'filename': backup.filename,
            'created_at': backup.created_at.isoformat(),
            'completed_at': backup.completed_at.isoformat() if backup.completed_at else None,
            'size': backup.size,
            'size_formatted': f"{backup.size / (1024 * 1024):.2f} MB" if backup.size else "0 MB",
        }
        return JsonResponse(data)
    except BackupFile.DoesNotExist:
        return JsonResponse({'error': 'Backup not found'}, status=404)

@login_required
@user_passes_test(is_admin_or_staff)
@csrf_exempt
def api_restore_status(request, restore_id):
    """API endpoint to check restore status"""
    try:
        restore_point = RestorePoint.objects.get(id=restore_id)
        data = {
            'id': str(restore_point.id),
            'status': restore_point.status,
            'name': restore_point.name,
            'created_at': restore_point.created_at.isoformat(),
            'restored_at': restore_point.restored_at.isoformat() if restore_point.restored_at else None,
        }
        return JsonResponse(data)
    except RestorePoint.DoesNotExist:
        return JsonResponse({'error': 'Restore point not found'}, status=404)
