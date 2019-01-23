# Generated by Django 2.1.1 on 2019-01-21 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0053_client_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='inactive_bc_link',
            field=models.CharField(blank=True, default=None, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='inactive_reason',
            field=models.IntegerField(choices=[(0, 'PO pending from client'), (1, 'Website being worked on'), (2, 'New budget pending from client'), (3, 'Other')], default=None, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='inactive_return_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
