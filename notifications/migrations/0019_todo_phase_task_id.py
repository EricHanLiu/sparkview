# Generated by Django 2.1.1 on 2019-06-11 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0018_auto_20190611_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='phase_task_id',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
