# Generated by Django 2.1.1 on 2019-07-29 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0081_merge_20190729_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionalfee',
            name='name',
            field=models.CharField(default='no name', max_length=255),
            preserve_default=False,
        ),
    ]