# Generated by Django 2.1.1 on 2018-12-05 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0026_auto_20181205_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backup',
            name='bc_link',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
