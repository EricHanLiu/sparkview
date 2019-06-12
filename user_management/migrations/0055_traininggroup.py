# Generated by Django 2.1.1 on 2019-06-12 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0054_skill_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255)),
                ('members', models.ManyToManyField(blank=True, default=None, null=True, to='user_management.Member')),
                ('roles', models.ManyToManyField(blank=True, default=None, null=True, to='user_management.Role')),
                ('skills', models.ManyToManyField(blank=True, default=None, null=True, to='user_management.Skill')),
            ],
        ),
    ]
