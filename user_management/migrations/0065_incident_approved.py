# Generated by Django 2.1.1 on 2019-07-04 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0064_auto_20190702_0739'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
