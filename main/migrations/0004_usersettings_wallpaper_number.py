# Generated by Django 4.2.6 on 2023-10-29 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_usersettings_thestart_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='wallpaper_number',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]