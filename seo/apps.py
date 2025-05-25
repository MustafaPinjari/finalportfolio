from django.apps import AppConfig

class SeoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seo'
    verbose_name = 'SEO Management'
    
    def ready(self):
        # Import signals or perform other initialization tasks
        pass
