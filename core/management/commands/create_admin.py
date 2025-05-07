from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a superuser'

    def handle(self, *args, **options):
        # Create a new superuser with a different username
        username = 'khatma_admin'
        email = 'khatma_admin@example.com'
        password = 'khatma123'

        # Check if this user already exists
        if User.objects.filter(username=username).exists():
            # Delete the existing user
            User.objects.filter(username=username).delete()
            self.stdout.write(self.style.WARNING(f'Deleted existing user: {username}'))

        # Create the new superuser
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(self.style.SUCCESS(f'Superuser created successfully: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
