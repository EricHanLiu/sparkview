# Generated by Django 2.1.1 on 2019-06-20 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0071_auto_20190619_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='text_excludes',
            field=models.CharField(blank=True, max_length=999),
        ),
        migrations.AlterField(
            model_name='budget',
            name='text_includes',
            field=models.CharField(blank=True, max_length=999),
        ),
    ]