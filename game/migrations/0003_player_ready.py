# Generated by Django 5.0.4 on 2024-05-20 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_rename_player_name_player_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='ready',
            field=models.BooleanField(default=False),
        ),
    ]
