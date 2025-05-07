from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_khatma_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='khatma',
            name='memorial_image',
            field=models.ImageField(blank=True, null=True, upload_to='memorial_images/', verbose_name='صورة تذكارية'),
        ),
        migrations.AddField(
            model_name='khatma',
            name='visibility',
            field=models.CharField(choices=[('public', 'عامة - متاحة للجميع'), ('private', 'خاصة - بدعوة فقط'), ('family', 'عائلية - للعائلة فقط')], default='public', max_length=20, verbose_name='خصوصية الختمة'),
        ),
        migrations.AddField(
            model_name='khatma',
            name='allow_comments',
            field=models.BooleanField(default=True, verbose_name='السماح بالتعليقات'),
        ),
        migrations.AddField(
            model_name='khatma',
            name='social_media_hashtags',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='وسوم التواصل الاجتماعي'),
        ),
        migrations.AddField(
            model_name='khatma',
            name='social_media_image',
            field=models.ImageField(blank=True, null=True, upload_to='social_media_images/', verbose_name='صورة للمشاركة'),
        ),
        migrations.AddField(
            model_name='khatma',
            name='max_participants',
            field=models.IntegerField(default=0, verbose_name='الحد الأقصى للمشاركين (0 = غير محدود)'),
        ),
        migrations.AddField(
            model_name='khatma',
            name='send_reminders',
            field=models.BooleanField(default=True, verbose_name='إرسال تذكيرات'),
        ),
        migrations.AddField(
            model_name='khatma',
            name='reminder_frequency',
            field=models.CharField(choices=[('daily', 'يومياً'), ('weekly', 'أسبوعياً'), ('never', 'لا ترسل')], default='weekly', max_length=20, verbose_name='تكرار التذكيرات'),
        ),
    ]
