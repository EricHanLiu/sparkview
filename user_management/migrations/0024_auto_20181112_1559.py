# Generated by Django 2.1.1 on 2018-11-12 15:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0023_auto_20181112_1431'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='member',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
