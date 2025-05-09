'''"""This module contains Module functionality."""'''
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    '''"""Class representing Command."""'''
    help = 'Set up the Site object for django-allauth'

    def handle(self, *args, **options):
        '''"""Function to handle."""'''
        domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
        site, created = Site.objects.get_or_create(pk=settings.SITE_ID, defaults={'domain': domain, 'name': 'Khatma App'})
        if not created:
            site.domain = domain
            site.name = 'Khatma App'
            site.save()
        self.stdout.write(self.style.SUCCESS(f"Successfully {('created' if created else 'updated')} Site: {site.domain}"))