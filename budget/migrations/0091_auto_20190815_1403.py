# Generated by Django 2.1.1 on 2019-08-15 19:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0090_budget_is_default'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['client_name']},
        ),
    ]
