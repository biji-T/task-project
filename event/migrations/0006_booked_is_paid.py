# Generated by Django 2.2.12 on 2021-12-01 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0005_auto_20211201_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='booked',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
    ]
