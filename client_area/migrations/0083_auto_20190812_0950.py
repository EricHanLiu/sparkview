# Generated by Django 2.1.1 on 2019-08-12 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0082_auto_20190627_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounthourrecord',
            name='is_onboarding',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mandatehourrecord',
            name='is_onboarding',
            field=models.BooleanField(default=False),
        ),
    ]
