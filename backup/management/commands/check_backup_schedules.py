from django.core.management.base import BaseCommand
from backup.tasks import check_backup_schedules

class Command(BaseCommand):
    help = 'Checks and runs any scheduled backups that are due'

    def handle(self, *args, **options):
        self.stdout.write('Checking for scheduled backups...')
        count = check_backup_schedules()
        self.stdout.write(self.style.SUCCESS(f'Completed checking scheduled backups. Ran {count} backup(s).'))
