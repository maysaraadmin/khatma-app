from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0006_fix_family_admin_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='family_admin',
            field=models.BooleanField(
                default=False,
                help_text='Designates whether user is a family admin',
                verbose_name='family admin'
            ),
        ),
    ]
