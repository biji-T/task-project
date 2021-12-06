# Generated by Django 2.2.12 on 2021-12-06 14:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0006_booked_is_paid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='events',
            options={'verbose_name': 'Event'},
        ),
        migrations.AlterField(
            model_name='booked',
            name='users',
            field=models.ManyToManyField(related_name='requirement_booked', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='dislike',
            name='users',
            field=models.ManyToManyField(related_name='requirement_dis_likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='like',
            name='users',
            field=models.ManyToManyField(related_name='requirement_likes', to=settings.AUTH_USER_MODEL),
        ),
    ]