# Generated by Django 2.1.1 on 2018-11-14 19:36

import django.contrib.postgres.fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0024_auto_20181112_1559'),
        ('notifications', '0004_auto_20181114_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulednotification',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='schedulednotification',
            name='day_of_week',
            field=models.IntegerField(blank=True, choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')], default=None, null=True),
        ),
        migrations.AddField(
            model_name='schedulednotification',
            name='days_negative',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, default=None, null=True, size=None),
        ),
        migrations.AddField(
            model_name='schedulednotification',
            name='days_positive',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, default=None, null=True, size=None),
        ),
        migrations.AddField(
            model_name='schedulednotification',
            name='link',
            field=models.URLField(blank=True, max_length=499),
        ),
        migrations.AddField(
            model_name='schedulednotification',
            name='message',
            field=models.CharField(default='No message', max_length=999),
        ),
        migrations.AddField(
            model_name='schedulednotification',
            name='roles',
            field=models.ManyToManyField(blank=True, default=None, to='user_management.Role'),
        ),
        migrations.AddField(
            model_name='schedulednotification',
            name='teams',
            field=models.ManyToManyField(blank=True, default=None, to='user_management.Team'),
        ),
    ]
