# Generated by Django 2.1.1 on 2019-07-02 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0063_auto_20190619_1309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skill',
            options={'ordering': ['skill_index']},
        ),
        migrations.AddField(
            model_name='skill',
            name='skill_index',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
