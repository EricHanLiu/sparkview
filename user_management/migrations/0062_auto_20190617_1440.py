# Generated by Django 2.1.1 on 2019-06-17 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0061_skillhistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backup',
            name='member',
        ),
        migrations.AddField(
            model_name='backup',
            name='members',
            field=models.ManyToManyField(blank=True, default=None, to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='skillentry',
            name='score',
            field=models.IntegerField(choices=[(0, 'Unscored'), (1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced'), (4, 'Expert')], default=0),
        ),
    ]