from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/favorites/', views.favorite_posts_view, name='favorite_posts'),
    path('profile/comments/', views.user_comments_view, name='user_comments'),
    # Notification settings removed as requested
    path('toggle-favorite/<int:post_id>/', views.toggle_favorite_post, name='toggle_favorite'),
    
    # Password reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),
         
    # Custom Admin Panel URLs
    path('admin/dashboard/', admin_views.custom_admin, name='custom_admin'),
    
    # User Management
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/users/create/', admin_views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:user_id>/edit/', admin_views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_id>/toggle-active/', admin_views.admin_user_toggle_active, name='admin_user_toggle_active'),
    
    # Post Management
    path('admin/posts/', admin_views.admin_posts, name='admin_posts'),
    path('admin/posts/create/', admin_views.admin_post_create, name='admin_post_create'),
    path('admin/posts/<slug:slug>/edit/', admin_views.admin_post_edit, name='admin_post_edit'),
    path('admin/posts/<slug:slug>/toggle-published/', admin_views.admin_post_toggle_published, name='admin_post_toggle_published'),
    path('admin/posts/<slug:slug>/delete/', admin_views.admin_post_delete, name='admin_post_delete'),
    
    # Comment Management
    path('admin/comments/', admin_views.admin_comments, name='admin_comments'),
    path('admin/comments/<int:comment_id>/toggle-approved/', admin_views.admin_comment_toggle_approved, name='admin_comment_toggle_approved'),
    path('admin/comments/<int:comment_id>/delete/', admin_views.admin_comment_delete, name='admin_comment_delete'),
    
    # Category Management
    path('admin/categories/', admin_views.admin_categories, name='admin_categories'),
    path('admin/categories/create/', admin_views.admin_category_create, name='admin_category_create'),
    path('admin/categories/<slug:slug>/edit/', admin_views.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/<slug:slug>/delete/', admin_views.admin_category_delete, name='admin_category_delete'),
    
    # Media and Settings
    path('admin/media/', admin_views.admin_media, name='admin_media'),
    path('admin/settings/', admin_views.admin_settings, name='admin_settings'),
    # Add these patterns to the existing urlpatterns
    path('admin/analytics/', admin_views.admin_analytics, name='admin_analytics'),
    path('admin/api/analytics/', admin_views.get_analytics_data, name='get_analytics_data'),
    
    # Notifications dashboard removed as requested
    
]
