# Generated by Django 2.1.1 on 2019-01-23 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0034_auto_20190118_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='onboardingstep',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='onboardingtaskassignment',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
