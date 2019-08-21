# Generated by Django 2.1.1 on 2019-08-07 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0088_auto_20190805_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='lost_reason',
            field=models.IntegerField(choices=[(0, 'Poor Performance'), (1, 'Mandate Over'), (2, 'Repeated Account Errors'), (3, 'Not a Good Fit (Mutual)'), (4, 'Internalized'), (5, 'Budget Issue'), (6, 'Changing Website'), (7, 'Changing Agency'), (8, 'Campaigns Never Started'), (9, 'Other (see Basecamp for details)')], default=None, null=True),
        ),
    ]