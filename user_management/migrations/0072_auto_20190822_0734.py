# Generated by Django 2.1.1 on 2019-08-22 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0071_auto_20190822_0730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='image',
            field=models.ImageField(null=True, upload_to='bloomers/'),
        ),
    ]
