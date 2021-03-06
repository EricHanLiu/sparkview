# Generated by Django 2.1.1 on 2018-11-14 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0024_auto_20181112_1559'),
        ('notifications', '0002_auto_20181114_1656'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('members', models.ManyToManyField(blank=True, default=None, null=True, to='user_management.Member')),
            ],
        ),
    ]
