# Generated by Django 2.1.1 on 2019-10-31 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0091_auto_20191031_0929'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberhourhistory',
            name='seniority_buffer',
            field=models.FloatField(default=0.0),
        ),
    ]
