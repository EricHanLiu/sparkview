# Generated by Django 2.1.1 on 2018-11-15 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_notification_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.IntegerField(blank=True, choices=[(0, 'Client related'), (1, 'Internal Request'), (2, 'Monthly Reminder'), (3, 'Reporting'), (4, 'Other')], default=5),
        ),
    ]
