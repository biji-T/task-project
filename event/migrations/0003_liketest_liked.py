# Generated by Django 2.2.12 on 2021-12-14 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_remove_liketest_liked'),
    ]

    operations = [
        migrations.AddField(
            model_name='liketest',
            name='liked',
            field=models.BooleanField(default=False),
        ),
    ]
