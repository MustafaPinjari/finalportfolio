from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from blog import views as blog_views
from .views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('backup/', include('backup.urls')),
    path('blog/', include('blog.urls')),
    path('users/', include('users.urls')),
    path('seo/', include('seo.urls')),
    path('projects/', include('projects.urls')),
    # Notifications removed as requested
    # Override allauth's login with our custom view
    path('accounts/login/', RedirectView.as_view(url='/users/login/', permanent=True)),
    path('accounts/signup/', RedirectView.as_view(url='/users/register/', permanent=True)),
    # Keep the rest of allauth URLs for social login functionality
    path('accounts/', include('allauth.urls')),
    path('', home, name='home'),
    path('contact/', blog_views.contact, name='contact'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
