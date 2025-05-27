# Create file: users/management/commands/setup_social_auth.py

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Sets up social authentication apps and site configuration'

    def handle(self, *args, **options):
        # Get or create production site
        prod_domain = 'mustafa-pinjari.onrender.com'
        site, created = Site.objects.get_or_create(
            domain=prod_domain,
            defaults={'name': 'Production Site'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created site: {prod_domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found existing site: {prod_domain}'))
        
        # Set up Google
        google_apps = SocialApp.objects.filter(provider='google')
        
        if google_apps.exists():
            # Clean up duplicates if any
            if google_apps.count() > 1:
                first_app = google_apps.first()
                for app in google_apps[1:]:
                    self.stdout.write(f'Deleting duplicate Google app: {app.name}')
                    app.delete()
                google_app = first_app
            else:
                google_app = google_apps.first()
                
            self.stdout.write(f'Using existing Google app: {google_app.name}')
        else:
            # Create new app
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id='YOUR_GOOGLE_CLIENT_ID',
                secret='YOUR_GOOGLE_SECRET'
            )
            self.stdout.write(self.style.SUCCESS(f'Created Google app: {google_app.name}'))
        
        # Ensure site is associated with app
        if site not in google_app.sites.all():
            google_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS(f'Associated Google app with site: {site.domain}'))
        
        # Verification
        self.stdout.write('\nVerification:')
        for app in SocialApp.objects.filter(provider='google'):
            sites = ', '.join(s.domain for s in app.sites.all())
            self.stdout.write(f'App {app.id}: {app.name}, sites: {sites}')