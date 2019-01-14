# Generated by Django 2.1.1 on 2019-01-14 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0051_auto_20190108_0953'),
        ('client_area', '0030_auto_20190108_1307'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnboardingTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.IntegerField(choices=[(0, 'PPC'), (1, 'SEO'), (2, 'CRO'), (3, 'Strategy')], default=0)),
                ('name', models.CharField(blank=True, default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OnboardingTaskAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('complete', models.BooleanField(default=False)),
                ('completed', models.DateTimeField(default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='budget.Client')),
                ('task', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='client_area.OnboardingTask')),
            ],
        ),
    ]
