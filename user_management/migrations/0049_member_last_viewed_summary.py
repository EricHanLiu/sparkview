# Generated by Django 2.1.1 on 2019-05-03 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0048_incident_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='last_viewed_summary',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]
