# Khatma Module Implementation Guide - Part 3

## 6. URL Configuration

### urls.py
```python
from django.urls import path
from . import views

app_name = 'khatma'

urlpatterns = [
    # Khatma management
    path('create/', views.create_khatma, name='create_khatma'),
    path('<int:khatma_id>/', views.khatma_detail, name='khatma_detail'),
    path('list/', views.khatma_list, name='khatma_list'),
    path('my-khatmas/', views.my_khatmas, name='my_khatmas'),
    path('<int:khatma_id>/edit/', views.edit_khatma, name='edit_khatma'),
    path('<int:khatma_id>/delete/', views.delete_khatma, name='delete_khatma'),
    path('<int:khatma_id>/complete/', views.complete_khatma, name='complete_khatma'),
    
    # Part management
    path('<int:khatma_id>/part/<int:part_id>/', views.part_detail, name='part_detail'),
    path('<int:khatma_id>/part/<int:part_id>/assign/', views.assign_part, name='assign_part'),
    path('<int:khatma_id>/part/<int:part_id>/complete/', views.complete_part, name='complete_part'),
    path('<int:khatma_id>/part/<int:part_id>/uncomplete/', views.uncomplete_part, name='uncomplete_part'),
    
    # Deceased management
    path('deceased/create/', views.create_deceased, name='create_deceased'),
    path('deceased/list/', views.deceased_list, name='deceased_list'),
    path('deceased/<int:deceased_id>/', views.deceased_detail, name='deceased_detail'),
    path('deceased/<int:deceased_id>/edit/', views.edit_deceased, name='edit_deceased'),
    path('deceased/<int:deceased_id>/delete/', views.delete_deceased, name='delete_deceased'),
    
    # Participant management
    path('<int:khatma_id>/join/', views.join_khatma, name='join_khatma'),
    path('<int:khatma_id>/leave/', views.leave_khatma, name='leave_khatma'),
    path('<int:khatma_id>/participants/', views.khatma_participants, name='khatma_participants'),
    path('<int:khatma_id>/remove-participant/<int:user_id>/', views.remove_participant, name='remove_participant'),
    
    # Sharing
    path('share/<uuid:sharing_link>/', views.shared_khatma, name='shared_khatma'),
    path('<int:khatma_id>/share/', views.share_khatma, name='share_khatma'),
    
    # API endpoints
    path('api/khatma/<int:khatma_id>/progress/', views.khatma_progress_api, name='khatma_progress_api'),
    path('api/khatma/<int:khatma_id>/part/<int:part_id>/status/', views.part_status_api, name='part_status_api'),
]
```

## 7. Admin Configuration

### admin.py
```python
from django.contrib import admin
from .models import Khatma, Deceased, Participant, KhatmaPart, PartAssignment, QuranReading


class KhatmaPartInline(admin.TabularInline):
    model = KhatmaPart
    extra = 0
    readonly_fields = ['part_number']


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0


@admin.register(Khatma)
class KhatmaAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'khatma_type', 'is_completed', 'created_at']
    list_filter = ['khatma_type', 'is_completed', 'frequency', 'visibility']
    search_fields = ['title', 'description', 'creator__username']
    date_hierarchy = 'created_at'
    inlines = [KhatmaPartInline, ParticipantInline]
    readonly_fields = ['sharing_link', 'created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'creator', 'description', 'khatma_type', 'frequency')
        }),
        ('Group Settings', {
            'fields': ('group', 'is_group_khatma', 'auto_distribute_parts')
        }),
        ('Memorial Settings', {
            'fields': ('deceased', 'memorial_prayer', 'memorial_image')
        }),
        ('Social Features', {
            'fields': ('is_public', 'visibility', 'allow_comments', 'social_media_hashtags', 'social_media_image')
        }),
        ('Status', {
            'fields': ('is_completed', 'target_completion_date', 'completed_at', 'start_date', 'end_date')
        }),
        ('Sharing and Participants', {
            'fields': ('sharing_link', 'max_participants')
        }),
        ('Reminders', {
            'fields': ('send_reminders', 'reminder_frequency')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Deceased)
class DeceasedAdmin(admin.ModelAdmin):
    list_display = ['name', 'death_date', 'added_by', 'memorial_day']
    list_filter = ['memorial_day', 'memorial_frequency']
    search_fields = ['name', 'biography', 'added_by__username']
    date_hierarchy = 'death_date'
    readonly_fields = ['created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'death_date', 'birth_date', 'photo', 'biography', 'added_by')
        }),
        ('Additional Information', {
            'fields': ('relation', 'cause_of_death', 'burial_place')
        }),
        ('Memorial Settings', {
            'fields': ('memorial_day', 'memorial_frequency')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(KhatmaPart)
class KhatmaPartAdmin(admin.ModelAdmin):
    list_display = ['khatma', 'part_number', 'assigned_to', 'is_completed', 'completed_at']
    list_filter = ['is_completed']
    search_fields = ['khatma__title', 'assigned_to__username']
    readonly_fields = ['completed_at']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'khatma', 'parts_read', 'joined_at']
    list_filter = ['joined_at']
    search_fields = ['user__username', 'khatma__title']
    readonly_fields = ['joined_at']


@admin.register(PartAssignment)
class PartAssignmentAdmin(admin.ModelAdmin):
    list_display = ['khatma', 'part', 'participant', 'is_completed', 'completed_at']
    list_filter = ['is_completed']
    search_fields = ['khatma__title', 'participant__username']
    readonly_fields = ['completed_at']


@admin.register(QuranReading)
class QuranReadingAdmin(admin.ModelAdmin):
    list_display = ['participant', 'khatma', 'part_number', 'status', 'start_date', 'completion_date']
    list_filter = ['status', 'recitation_method']
    search_fields = ['participant__username', 'khatma__title', 'notes', 'dua']
    date_hierarchy = 'start_date'
    readonly_fields = ['reading_duration']
```

## 8. Signal Handlers

### signals.py
```python
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Khatma, KhatmaPart, QuranReading, Deceased
from notifications.models import Notification
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
        Notification.objects.create(
            user=khatma.creator,
            notification_type='khatma_completed',
            message=f'تم إكمال الختمة: {khatma.title}',
            related_khatma=khatma
        )


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
    Notification.objects.create(
        user=deceased.added_by,
        notification_type='memorial_khatma',
        message=f'تم إنشاء ختمة تذكارية للمتوفى: {deceased.name}',
        related_khatma=khatma
    )
    
    return khatma
```

## 9. Template Example

### templates/khatma/khatma_detail.html
```html
{% extends "core/base.html" %}
{% load static %}

{% block title %}{{ khatma.title }} - تفاصيل الختمة{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card shadow-sm">
        <div class="card-header bg-primary text-white">
            <h2 class="mb-0">{{ khatma.title }}</h2>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-8">
                    <p class="text-muted">{{ khatma.description }}</p>
                    
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div>
                            <span class="badge bg-secondary">{{ khatma.get_khatma_type_display }}</span>
                            <span class="badge bg-info">{{ khatma.get_frequency_display }}</span>
                            {% if khatma.is_completed %}
                                <span class="badge bg-success">مكتملة</span>
                            {% else %}
                                <span class="badge bg-warning">قيد التنفيذ</span>
                            {% endif %}
                        </div>
                        <small class="text-muted">تم الإنشاء: {{ khatma.created_at|date:"Y-m-d" }}</small>
                    </div>
                    
                    {% if khatma.deceased %}
                    <div class="alert alert-info">
                        <h5>ختمة تذكارية للمتوفى:</h5>
                        <div class="d-flex align-items-center">
                            {% if khatma.deceased.photo %}
                                <img src="{{ khatma.deceased.photo.url }}" alt="{{ khatma.deceased.name }}" class="rounded-circle me-3" style="width: 50px; height: 50px; object-fit: cover;">
                            {% endif %}
                            <div>
                                <h6 class="mb-0">{{ khatma.deceased.name }}</h6>
                                <small>{{ khatma.deceased.death_date|date:"Y-m-d" }}</small>
                            </div>
                        </div>
                        {% if khatma.memorial_prayer %}
                            <div class="mt-2">
                                <p class="mb-0"><strong>دعاء:</strong> {{ khatma.memorial_prayer }}</p>
                            </div>
                        {% endif %}
                    </div>
                    {% endif %}
                    
                    <!-- Progress bar -->
                    <div class="progress mb-3" style="height: 25px;">
                        <div class="progress-bar bg-success" role="progressbar" style="width: {{ progress_percentage }}%;" 
                             aria-valuenow="{{ progress_percentage }}" aria-valuemin="0" aria-valuemax="100">
                            {{ progress_percentage|floatformat:1 }}%
                        </div>
                    </div>
                    <p class="text-center">{{ completed_parts }} من {{ total_parts }} جزء مكتمل</p>
                    
                    {% if not is_participant and not khatma.is_completed %}
                        <form method="post">
                            {% csrf_token %}
                            <button type="submit" class="btn btn-primary btn-block">انضم إلى الختمة</button>
                        </form>
                    {% endif %}
                </div>
                
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header bg-light">
                            <h5 class="mb-0">معلومات الختمة</h5>
                        </div>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item d-flex justify-content-between">
                                <span>منشئ الختمة:</span>
                                <span>{{ khatma.creator.username }}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span>عدد المشاركين:</span>
                                <span>{{ khatma.participants.count }}</span>
                            </li>
                            {% if khatma.target_completion_date %}
                            <li class="list-group-item d-flex justify-content-between">
                                <span>تاريخ الإكمال المستهدف:</span>
                                <span>{{ khatma.target_completion_date|date:"Y-m-d" }}</span>
                            </li>
                            {% endif %}
                            {% if khatma.is_completed and khatma.completed_at %}
                            <li class="list-group-item d-flex justify-content-between">
                                <span>تم الإكمال في:</span>
                                <span>{{ khatma.completed_at|date:"Y-m-d" }}</span>
                            </li>
                            {% endif %}
                        </ul>
                    </div>
                    
                    {% if is_creator %}
                    <div class="mt-3">
                        <a href="{% url 'khatma:edit_khatma' khatma.id %}" class="btn btn-outline-primary btn-sm mb-2 w-100">تعديل الختمة</a>
                        <a href="{% url 'khatma:share_khatma' khatma.id %}" class="btn btn-outline-success btn-sm mb-2 w-100">مشاركة الختمة</a>
                        <a href="{% url 'khatma:khatma_participants' khatma.id %}" class="btn btn-outline-info btn-sm mb-2 w-100">إدارة المشاركين</a>
                        {% if not khatma.is_completed %}
                            <a href="{% url 'khatma:complete_khatma' khatma.id %}" class="btn btn-outline-success btn-sm mb-2 w-100">إكمال الختمة</a>
                        {% endif %}
                        <a href="{% url 'khatma:delete_khatma' khatma.id %}" class="btn btn-outline-danger btn-sm w-100">حذف الختمة</a>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Parts grid -->
            <h4 class="mt-4 mb-3">أجزاء الختمة</h4>
            <div class="row row-cols-2 row-cols-md-5 g-3">
                {% for part in parts %}
                <div class="col">
                    <div class="card h-100 {% if part.is_completed %}border-success{% endif %}">
                        <div class="card-body text-center">
                            <h5 class="card-title">الجزء {{ part.part_number }}</h5>
                            {% if part.assigned_to %}
                                <p class="card-text small mb-1">{{ part.assigned_to.username }}</p>
                            {% endif %}
                            {% if part.is_completed %}
                                <span class="badge bg-success">مكتمل</span>
                            {% elif part.assigned_to %}
                                <span class="badge bg-warning">قيد التنفيذ</span>
                            {% else %}
                                <span class="badge bg-secondary">غير معين</span>
                            {% endif %}
                        </div>
                        <div class="card-footer bg-transparent">
                            <a href="{% url 'khatma:part_detail' khatma.id part.part_number %}" class="btn btn-sm btn-outline-primary w-100">التفاصيل</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```
