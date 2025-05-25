from django.urls import path
from . import views

app_name = 'seo'

urlpatterns = [
    # SEO Dashboard
    path('admin/seo/', views.admin_seo_dashboard, name='dashboard'),
    
    # SEO Metadata Editor
    path('admin/seo/edit/<int:content_type_id>/<int:object_id>/', views.edit_seo_metadata, name='edit_metadata'),
    
    # SEO Analysis
    path('admin/seo/analyze/<int:metadata_id>/', views.run_analysis, name='run_analysis'),
    
    # Resolve Issue
    path('admin/seo/issue/<int:issue_id>/resolve/', views.resolve_issue, name='resolve_issue'),
    
    # Sitemap Management
    path('admin/seo/sitemap/', views.manage_sitemap, name='manage_sitemap'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    
    # Keyword Analysis
    path('admin/seo/keywords/', views.keyword_analysis, name='keyword_analysis'),
    
    # Real-time SEO Check
    path('admin/seo/check/', views.real_time_seo_check, name='real_time_check'),
]
