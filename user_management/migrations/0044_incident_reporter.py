# Generated by Django 2.1.1 on 2019-04-30 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0043_auto_20190430_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='reporter',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reporter', to='user_management.Member'),
        ),
    ]
