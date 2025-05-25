from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for AllAuth to override login/signup URLs
    and use our custom templates instead of the default ones.
    """
    def get_login_redirect_url(self, request):
        """
        Override to handle admin users differently
        """
        # Check if user is staff and redirect to admin dashboard if so
        if request.user.is_authenticated and request.user.is_staff:
            return reverse('custom_admin')
        return settings.LOGIN_REDIRECT_URL
    
    def get_signup_redirect_url(self, request):
        """
        Where to redirect after signup
        """
        return settings.LOGIN_REDIRECT_URL

    def logout(self, request):
        """
        Override to customize logout behavior
        """
        from django.contrib.auth import logout
        logout(request)
        return
