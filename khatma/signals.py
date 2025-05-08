from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Khatma, KhatmaPart, QuranReading, Deceased
import datetime


@receiver(post_save, sender=Khatma)
def create_khatma_parts(sender, instance, created, **kwargs):
    """Create parts for a new Khatma"""
    if created:
        # Create 30 parts for the Khatma
        for i in range(1, 31):
            KhatmaPart.objects.create(
                khatma=instance,
                part_number=i
            )


@receiver(post_save, sender=KhatmaPart)
def update_khatma_completion(sender, instance, **kwargs):
    """Update Khatma completion status when a part is completed"""
    khatma = instance.khatma
    
    # Check if all parts are completed
    all_parts_completed = not KhatmaPart.objects.filter(khatma=khatma, is_completed=False).exists()
    
    if all_parts_completed and not khatma.is_completed:
        # Mark Khatma as completed
        khatma.is_completed = True
        khatma.completed_at = timezone.now()
        khatma.save()
        
        # Create notification for Khatma completion
        try:
            from notifications.models import Notification
            Notification.objects.create(
                user=khatma.creator,
                notification_type='khatma_completed',
                message=f'تم إكمال الختمة: {khatma.title}',
                related_khatma=khatma
            )
        except ImportError:
            pass  # Notifications module not available


@receiver(pre_save, sender=KhatmaPart)
def update_part_completion_date(sender, instance, **kwargs):
    """Set completion date when a part is marked as completed"""
    if instance.pk:  # Only for existing instances
        try:
            old_instance = KhatmaPart.objects.get(pk=instance.pk)
            if not old_instance.is_completed and instance.is_completed:
                instance.completed_at = timezone.now()
        except KhatmaPart.DoesNotExist:
            pass


@receiver(post_save, sender=QuranReading)
def update_participant_parts_read(sender, instance, **kwargs):
    """Update participant's parts_read count when a reading is completed"""
    if instance.status == 'completed':
        participant = instance.participant
        khatma = instance.khatma
        
        # Get participant record
        try:
            from .models import Participant
            participant_record = Participant.objects.get(user=participant, khatma=khatma)
            
            # Count completed readings
            completed_readings = QuranReading.objects.filter(
                participant=participant,
                khatma=khatma,
                status='completed'
            ).count()
            
            # Update parts_read
            participant_record.parts_read = completed_readings
            participant_record.save()
        except Participant.DoesNotExist:
            pass


@receiver(post_save, sender=Deceased)
def schedule_memorial_khatma(sender, instance, created, **kwargs):
    """Schedule memorial Khatma if memorial_day is enabled"""
    if instance.memorial_day:
        # Check if we need to create a memorial Khatma
        today = timezone.now().date()
        
        # For yearly memorials, check if today is the anniversary
        if instance.memorial_frequency == 'yearly':
            if today.month == instance.death_date.month and today.day == instance.death_date.day:
                create_memorial_khatma(instance)
        
        # For monthly memorials, check if today is the monthly anniversary
        elif instance.memorial_frequency == 'monthly':
            if today.day == instance.death_date.day:
                create_memorial_khatma(instance)
        
        # For weekly memorials, check if today is the weekly anniversary
        elif instance.memorial_frequency == 'weekly':
            if (today - instance.death_date).days % 7 == 0:
                create_memorial_khatma(instance)
        
        # For daily memorials, create a new Khatma every day
        elif instance.memorial_frequency == 'daily':
            create_memorial_khatma(instance)


def create_memorial_khatma(deceased):
    """Helper function to create a memorial Khatma"""
    # Create a new memorial Khatma
    today = timezone.now().date()
    years_since_death = today.year - deceased.death_date.year
    
    khatma = Khatma.objects.create(
        title=f'ختمة تذكارية: {deceased.name} - الذكرى {years_since_death}',
        creator=deceased.added_by,
        description=f'ختمة تذكارية في ذكرى وفاة {deceased.name}',
        khatma_type='memorial',
        deceased=deceased,
        is_public=True,
        visibility='public',
        start_date=today,
        target_completion_date=today + datetime.timedelta(days=30)
    )
    
    # Create notification for memorial Khatma
    try:
        from notifications.models import Notification
        Notification.objects.create(
            user=deceased.added_by,
            notification_type='memorial_khatma',
            message=f'تم إنشاء ختمة تذكارية للمتوفى: {deceased.name}',
            related_khatma=khatma
        )
    except ImportError:
        pass  # Notifications module not available
    
    return khatma
