from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    # Dashboard
    path('', views.admin_backup_dashboard, name='dashboard'),
    
    # Backup management
    path('backups/', views.backup_list, name='backup_list'),
    path('backups/create/', views.create_manual_backup, name='create_manual_backup'),
    path('backups/import/', views.import_backup_view, name='import_backup'),
    path('backups/<uuid:backup_id>/', views.backup_detail, name='backup_detail'),
    path('backups/<uuid:backup_id>/download/', views.backup_download, name='backup_download'),
    path('backups/<uuid:backup_id>/delete/', views.backup_delete, name='backup_delete'),
    
    # Schedule management
    path('schedules/', views.manage_backup_schedules, name='manage_backup_schedules'),
    path('schedules/create/', views.create_backup_schedule, name='create_backup_schedule'),
    path('schedules/<int:schedule_id>/edit/', views.edit_backup_schedule, name='edit_backup_schedule'),
    path('schedules/<int:schedule_id>/delete/', views.delete_backup_schedule, name='delete_backup_schedule'),
    
    # Restore management
    path('restores/', views.restore_list, name='restore_list'),
    path('restores/create/', views.create_restore_point, name='create_restore_point'),
    path('restores/<uuid:restore_id>/', views.restore_detail, name='restore_detail'),
    path('restores/<uuid:restore_id>/execute/', views.execute_restore, name='execute_restore'),
    path('restores/<uuid:restore_id>/delete/', views.delete_restore_point, name='delete_restore_point'),
    
    # API endpoints
    path('api/backups/<uuid:backup_id>/status/', views.api_backup_status, name='api_backup_status'),
    path('api/restores/<uuid:restore_id>/status/', views.api_restore_status, name='api_restore_status'),
]
