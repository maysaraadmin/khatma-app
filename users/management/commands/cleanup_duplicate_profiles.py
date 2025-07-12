from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile

class Command(BaseCommand):
    help = 'Clean up duplicate user profiles and keep the first one for each user'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Find all users with duplicate profiles
        from django.db.models import Count
        duplicate_users = User.objects.annotate(
            profile_count=Count('profile')
        ).filter(profile_count__gt=1)
        
        for user in duplicate_users:
            self.stdout.write(f'Processing user: {user.username} (ID: {user.id})')
            
            # Get all profiles for this user except the first one
            profiles = Profile.objects.filter(user=user).order_by('id')
            if profiles.count() > 1:
                # Keep the first profile
                first_profile = profiles.first()
                self.stdout.write(f'  Keeping profile ID: {first_profile.id}')
                
                # Delete all other profiles
                for profile in profiles[1:]:
                    self.stdout.write(f'  Deleting duplicate profile ID: {profile.id}')
                    profile.delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully cleaned up duplicate profiles'))
