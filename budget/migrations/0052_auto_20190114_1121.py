# Generated by Django 2.1.1 on 2019-01-14 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0051_auto_20190108_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='has_ppc',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='client',
            name='has_strat',
            field=models.BooleanField(default=False),
        ),
    ]
