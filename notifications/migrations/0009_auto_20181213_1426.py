# Generated by Django 2.1.1 on 2018-12-13 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0008_auto_20181116_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulednotification',
            name='every_day',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedulednotification',
            name='every_week_day',
            field=models.BooleanField(default=False),
        ),
    ]
