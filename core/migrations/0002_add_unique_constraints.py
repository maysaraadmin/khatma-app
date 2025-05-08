from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readinggroup',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='اسم المجموعة'),
        ),
        migrations.AlterField(
            model_name='quranreciter',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='اسم القارئ'),
        ),
        migrations.AlterField(
            model_name='quranreciter',
            name='name_arabic',
            field=models.CharField(max_length=100, unique=True, verbose_name='اسم القارئ بالعربية'),
        ),
        migrations.AlterField(
            model_name='khatma',
            name='title',
            field=models.CharField(max_length=200, unique=True, verbose_name='عنوان الختمة'),
        ),
        migrations.AlterField(
            model_name='deceased',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='اسم المتوفى'),
        ),
        migrations.AlterField(
            model_name='khatmacommunitypost',
            name='title',
            field=models.CharField(max_length=200, unique=True, verbose_name='عنوان المنشور'),
        ),
        migrations.AlterModelOptions(
            name='ayah',
            options={'ordering': ['surah', 'ayah_number_in_surah'], 'verbose_name': 'آية', 'verbose_name_plural': 'آيات'},
        ),
        migrations.AlterModelOptions(
            name='quranbookmark',
            options={'verbose_name': 'إشارة مرجعية', 'verbose_name_plural': 'إشارات مرجعية'},
        ),
        migrations.AlterUniqueTogether(
            name='ayah',
            unique_together={('surah', 'ayah_number_in_surah')},
        ),
        migrations.AlterUniqueTogether(
            name='quranbookmark',
            unique_together={('user', 'ayah')},
        ),
    ]
