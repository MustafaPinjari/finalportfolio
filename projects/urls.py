from django.urls import path
from . import views
from . import admin_views

app_name = 'projects'

urlpatterns = [
    path('', views.projects, name='projects_list'),
    
    # Admin routes - must come before the catch-all slug pattern
    path('admin/', admin_views.admin_projects, name='admin_projects'),
    path('admin/add/', admin_views.admin_project_form, name='admin_project_add'),
    path('admin/edit/<int:project_id>/', admin_views.admin_project_form, name='admin_project_edit'),
    path('admin/delete/<int:project_id>/', admin_views.delete_project, name='admin_project_delete'),
    path('admin/screenshots/<int:project_id>/', admin_views.admin_project_screenshots, name='admin_project_screenshots'),
    
    # Detail view - must come after specific routes to avoid conflicts
    path('<slug:slug>/', views.project_detail, name='project_detail'),
]
