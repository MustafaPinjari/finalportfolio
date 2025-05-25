from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.utils import timezone
from .models import PageView, UserActivity
from .websocket import broadcast_visitor_update

class ImageOptimizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if not request.path.startswith('/admin') and not request.path.startswith('/static'):
            PageView.objects.create(
                path=request.path,
                ip_address=self.get_client_ip(request),
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key
            )
        
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method == 'POST' and request.FILES:
            for field in request.FILES:
                image = request.FILES[field]
                if self._is_image(image):
                    optimized = self._optimize_image(image)
                    request.FILES[field] = optimized
        return None

    def _is_image(self, file):
        try:
            Image.open(file)
            file.seek(0)
            return True
        except:
            return False

    def _optimize_image(self, image):
        img = Image.open(image)
        
        # Convert to RGB if necessary
        if img.mode not in ('L', 'RGB'):
            img = img.convert('RGB')
        
        # Resize if too large
        max_size = (1200, 1200)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)
        
        # Save with optimization
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        return InMemoryUploadedFile(output,
                                  'ImageField',
                                  f"{image.name.split('.')[0]}.jpg",
                                  'image/jpeg',
                                  sys.getsizeof(output),
                                  None)
class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Track page views for analytics, excluding admin and static files
        if not request.path.startswith('/admin') and not request.path.startswith('/static'):
            # Create page view record
            PageView.objects.create(
                path=request.path,
                ip_address=self.get_client_ip(request),
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key
            )
            
            # Track user activity if authenticated
            if request.user.is_authenticated:
                UserActivity.objects.create(
                    user=request.user,
                    action_type='page_view',
                    timestamp=timezone.now()
                )
            
            # Broadcast update to real-time analytics dashboard
            try:
                broadcast_visitor_update()
            except Exception as e:
                # Silently fail if websocket not available yet
                pass
        
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')