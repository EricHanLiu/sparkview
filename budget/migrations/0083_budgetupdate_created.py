# Generated by Django 2.1.1 on 2019-07-29 20:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0082_additionalfee_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetupdate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
