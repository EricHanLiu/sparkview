# Generated by Django 2.1.1 on 2018-11-14 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_schedulednotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulednotification',
            name='members',
            field=models.ManyToManyField(blank=True, default=None, to='user_management.Member'),
        ),
    ]
