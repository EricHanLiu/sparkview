# Generated by Django 2.1.1 on 2019-06-07 13:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adwords_dashboard', '0012_badad'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadAdAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0)),
                ('label', models.CharField(default='', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='adwords_dashboard.DependentAccount')),
            ],
        ),
    ]
