# Generated by Django 2.1.1 on 2019-04-18 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0066_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='mandatetype',
            name='hourly_rate',
            field=models.FloatField(default=125.0),
        ),
    ]
