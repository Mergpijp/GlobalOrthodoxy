# Generated by Django 2.2.13 on 2021-01-27 12:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0090_merge_20210127_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
