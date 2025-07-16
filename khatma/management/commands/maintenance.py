""
Management command for performing maintenance tasks.
"""
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from khatma.models import Khatma, Participant, KhatmaPart, QuranReading

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Perform maintenance tasks for the Khatma application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old or incomplete data',
        )
        parser.add_argument(
            '--notify',
            action='store_true',
            help='Send notifications for upcoming or overdue tasks',
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create a backup of the database',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all maintenance tasks',
        )

    def handle(self, *args, **options):
        """Handle the command."""
        self.stdout.write(self.style.SUCCESS('Starting maintenance tasks...'))
        
        if options['all'] or options['cleanup']:
            self.cleanup_data()
        
        if options['all'] or options['notify']:
            self.send_notifications()
        
        if options['all'] or options['backup']:
            self.create_backup()
        
        self.stdout.write(self.style.SUCCESS('Maintenance tasks completed successfully'))
    
    def cleanup_data(self):
        """Clean up old or incomplete data."""
        self.stdout.write('Cleaning up old or incomplete data...')
        
        # Delete incomplete khatmas older than 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        deleted_count, _ = Khatma.objects.filter(
            created_at__lt=thirty_days_ago,
            is_completed=False,
            participants__isnull=True
        ).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {deleted_count} old incomplete khatmas')
        )
        
        # Clean up abandoned participants (users who never completed setup)
        abandoned_participants = Participant.objects.filter(
            joined_at__lt=timezone.now() - timedelta(days=7),
            parts_read=0
        )
        abandoned_count = abandoned_participants.count()
        abandoned_participants.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Removed {abandoned_count} abandoned participants')
        )
        
        # Clean up old completed khatmas (configurable retention period)
        retention_days = getattr(settings, 'KHATMA_RETENTION_DAYS', 365)
        if retention_days > 0:
            retention_date = timezone.now() - timedelta(days=retention_days)
            old_completed = Khatma.objects.filter(
                is_completed=True,
                completed_at__lt=retention_date
            )
            old_count = old_completed.count()
            old_completed.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'Cleaned up {old_count} old completed khatmas')
            )
    
    def send_notifications(self):
        """Send notifications for upcoming or overdue tasks."""
        self.stdout.write('Sending notifications...')
        
        # Notify users about upcoming khatma deadlines
        upcoming_deadline = timezone.now() + timedelta(days=3)
        upcoming_khatmas = Khatma.objects.filter(
            is_completed=False,
            target_completion_date__lte=upcoming_deadline,
            target_completion_date__gte=timezone.now()
        )
        
        for khatma in upcoming_khatmas:
            participants = khatma.participants.all()
            for participant in participants:
                # In a real implementation, this would send an email or push notification
                self.stdout.write(
                    f'Notifying {participant.user.username} about upcoming deadline for khatma {khatma.id}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Sent notifications for {upcoming_khatmas.count()} khatmas')
        )
        
        # Notify about overdue khatmas
        overdue_khatmas = Khatma.objects.filter(
            is_completed=False,
            target_completion_date__lt=timezone.now()
        )
        
        for khatma in overdue_khatmas:
            # In a real implementation, this would send an email or push notification
            self.stdout.write(
                f'Khatma {khatma.id} is overdue!'
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {overdue_khatmas.count()} overdue khatmas')
        )
    
    def create_backup(self):
        """Create a backup of the database."""
        self.stdout.write('Creating database backup...')
        
        # This is a simplified example - in production, you would use a proper backup solution
        # like django-dbbackup or a database-specific tool
        
        backup_dir = getattr(settings, 'BACKUP_DIR', '/var/backups/khatma')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{backup_dir}/khatma_db_{timestamp}.sql'
        
        # Ensure the backup directory exists
        import os
        os.makedirs(backup_dir, exist_ok=True)
        
        # This is a simplified example - in production, use a proper database backup command
        self.stdout.write(f'Backup would be saved to: {backup_file}')
        self.stdout.write('Note: Actual backup implementation depends on your database')
        
        # Example for PostgreSQL (uncomment and customize as needed):
        # import subprocess
        # try:
        #     subprocess.run([
        #         'pg_dump',
        #         '-h', settings.DATABASES['default']['HOST'],
        #         '-U', settings.DATABASES['default']['USER'],
        #         '-d', settings.DATABASES['default']['NAME'],
        #         '-f', backup_file,
        #         '-F', 'c',  # Custom format (compressed)
        #     ], check=True)
        #     self.stdout.write(self.style.SUCCESS('Database backup created successfully'))
        # except subprocess.CalledProcessError as e:
        #     self.stderr.write(self.style.ERROR(f'Error creating database backup: {e}'))
        
        self.stdout.write(
            self.style.SUCCESS('Database backup process completed (see notes above)')
        )
