# Generated by Django 2.1.1 on 2019-08-20 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0068_merge_20190819_1044'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skill',
            options={'ordering': ['skill_category__name']},
        ),
        migrations.RemoveField(
            model_name='skill',
            name='skill_index',
        ),
    ]
