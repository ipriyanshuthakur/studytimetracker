# Generated by Django 4.2.6 on 2023-10-29 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_usersettings_wallpaper_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersettings',
            name='wallpaper_number',
        ),
        migrations.AddField(
            model_name='usersettings',
            name='wallpaper_name',
            field=models.CharField(default='wall0.png', max_length=100),
        ),
    ]
