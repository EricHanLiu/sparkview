# Generated by Django 2.1.1 on 2019-05-01 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0047_auto_20190501_0923'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='timestamp',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]