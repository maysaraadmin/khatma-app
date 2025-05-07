from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deceased',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='تاريخ الميلاد'),
        ),
    ]
