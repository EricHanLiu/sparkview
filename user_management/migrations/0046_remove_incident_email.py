# Generated by Django 2.1.1 on 2019-05-01 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0045_incident_addressed_with_member'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incident',
            name='email',
        ),
    ]
