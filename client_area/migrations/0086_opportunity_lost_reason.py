# Generated by Django 2.1.1 on 2019-08-13 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0085_opportunity_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='lost_reason',
            field=models.CharField(blank=True, default='', max_length=900),
        ),
    ]
