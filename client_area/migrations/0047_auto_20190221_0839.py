# Generated by Django 2.1.1 on 2019-02-21 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0046_auto_20190220_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='lifecycleevent',
            name='notes',
            field=models.CharField(blank=True, default='', max_length=999),
        ),
        migrations.AlterField(
            model_name='lifecycleevent',
            name='type',
            field=models.IntegerField(choices=[(1, 'Account won'), (2, 'Onboarding complete'), (3, 'Account inactive'), (4, 'Account active'), (5, 'Account lost'), (6, 'Upsell attempt'), (7, '90 days task complete'), (8, 'Account flagged'), (9, 'Other'), (10, 'Member assigned to flagged account'), (11, 'Changed assigned members'), (12, 'Late to onboard')], default=1),
        ),
    ]