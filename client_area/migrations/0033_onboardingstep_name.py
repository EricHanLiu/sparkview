# Generated by Django 2.1.1 on 2019-01-14 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0032_auto_20190114_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='onboardingstep',
            name='name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
