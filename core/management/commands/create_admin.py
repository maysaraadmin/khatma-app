'''"""This module contains Module functionality."""'''
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    '''"""Class representing Command."""'''
    help = 'Create a superuser'

    def handle(self, *args, **options):
        '''"""Function to handle."""'''
        username = 'khatma_admin'
        email = 'khatma_admin@example.com'
        password = 'khatma123'
        if User.objects.filter(username=username).exists():
            User.objects.filter(username=username).delete()
            self.stdout.write(self.style.WARNING(f'Deleted existing user: {username}'))
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser created successfully: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Password: {password}'))