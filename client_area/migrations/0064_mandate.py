# Generated by Django 2.1.1 on 2019-04-17 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0037_memberhourhistory'),
        ('budget', '0063_auto_20190329_1347'),
        ('client_area', '0063_mandatetype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mandate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='budget.Client')),
                ('mandate_type', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='client_area.MandateType')),
                ('members', models.ManyToManyField(blank=True, to='user_management.Member')),
            ],
        ),
    ]