# Generated by Django 2.1.1 on 2019-10-24 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0091_monthlyreport_date_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountallocatedhourshistory',
            name='worked_hours',
            field=models.FloatField(default=0.0),
        ),
    ]