from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_alter_profile_options_alter_userachievement_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='family_admin',
            field=models.BooleanField(
                default=False,
                help_text='Designates whether the user is a family admin',
                verbose_name='family admin'
            ),
        ),
    ]
