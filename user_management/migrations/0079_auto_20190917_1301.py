# Generated by Django 2.1.1 on 2019-09-17 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0078_auto_20190917_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='internaloops',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
