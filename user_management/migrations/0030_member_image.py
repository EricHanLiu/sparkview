# Generated by Django 2.1.1 on 2018-12-14 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0029_traininghoursrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='image',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
