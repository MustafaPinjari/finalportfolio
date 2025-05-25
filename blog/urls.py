from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    # Fixed order - specific routes before wildcard routes
    path('post/<int:post_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    # Admin routes - MUST be before the catch-all slug pattern
    path('admin/', views.admin_blog, name='admin_blog'),
    # This should be last because it's a catch-all for slugs
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
]
