# Generated by Django 2.1.1 on 2019-06-11 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0079_pitch_opportunity'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='addressed',
            field=models.BooleanField(default=False),
        ),
    ]
