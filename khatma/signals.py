"""Signal handlers for the khatma app."""
import datetime

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Khatma, KhatmaPart, Participant, QuranReading, Deceased
from notifications.models import Notification


@receiver(post_save, sender=Khatma)
def create_khatma_parts(sender, instance, created, **kwargs):
    """Create the Quran parts for a new Khatma (defaults to 30 juz)."""
    if not created:
        return
    from quran.models import QuranPart

    total_parts = QuranPart.objects.count() or 30
    if KhatmaPart.objects.filter(khatma=instance).exists():
        return
    KhatmaPart.objects.bulk_create([
        KhatmaPart(khatma=instance, part_number=i)
        for i in range(1, total_parts + 1)
    ])


@receiver(post_save, sender=KhatmaPart)
def update_khatma_completion(sender, instance, **kwargs):
    """Mark the Khatma complete once all of its parts are completed."""
    if not instance.is_completed:
        return
    khatma = instance.khatma
    if khatma.is_completed:
        return
    all_parts_completed = not KhatmaPart.objects.filter(
        khatma=khatma, is_completed=False
    ).exists()
    if all_parts_completed:
        khatma.is_completed = True
        khatma.completed_at = timezone.now()
        khatma.save(update_fields=['is_completed', 'completed_at'])
        Notification.objects.create(
            user=khatma.creator,
            notification_type='khatma_completed',
            message=f'تم إكمال الختمة: {khatma.title}',
            related_khatma=khatma,
        )


@receiver(pre_save, sender=KhatmaPart)
def update_part_completion_date(sender, instance, **kwargs):
    """Set the completion date only when a part is freshly completed."""
    if not (instance.pk and instance.is_completed):
        return
    try:
        old_instance = KhatmaPart.objects.only('is_completed').get(pk=instance.pk)
    except KhatmaPart.DoesNotExist:
        return
    if not old_instance.is_completed:
        instance.completed_at = timezone.now()


@receiver(post_save, sender=QuranReading)
def update_participant_parts_read(sender, instance, **kwargs):
    """Keep the participant's completed-parts count in sync."""
    if instance.status != 'completed':
        return
    try:
        participant_record = Participant.objects.get(
            user=instance.participant, khatma=instance.khatma
        )
    except Participant.DoesNotExist:
        return
    completed_readings = QuranReading.objects.filter(
        participant=instance.participant, khatma=instance.khatma, status='completed'
    ).count()
    participant_record.parts_read = completed_readings
    participant_record.save(update_fields=['parts_read'])


@receiver(post_save, sender=Deceased)
def schedule_memorial_khatma(sender, instance, created, **kwargs):
    """Schedule a memorial Khatma when memorial_day is enabled."""
    if not instance.memorial_day:
        return
    today = timezone.now().date()
    if instance.memorial_frequency == 'yearly':
        if today.month == instance.death_date.month and today.day == instance.death_date.day:
            create_memorial_khatma(instance)
    elif instance.memorial_frequency == 'monthly':
        if today.day == instance.death_date.day:
            create_memorial_khatma(instance)
    elif instance.memorial_frequency == 'weekly':
        if (today - instance.death_date).days % 7 == 0:
            create_memorial_khatma(instance)
    elif instance.memorial_frequency == 'daily':
        create_memorial_khatma(instance)


def create_memorial_khatma(deceased):
    """Create a memorial Khatma for a deceased person."""
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
        target_completion_date=today + datetime.timedelta(days=30),
    )
    Notification.objects.create(
        user=deceased.added_by,
        notification_type='memorial_khatma',
        message=f'تم إنشاء ختمة تذكارية للمتوفى: {deceased.name}',
        related_khatma=khatma,
    )
    return khatma
