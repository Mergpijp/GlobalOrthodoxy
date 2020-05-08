# Generated by Django 2.2.10 on 2020-04-20 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0059_auto_20200316_1057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='image_details',
        ),
        migrations.AddField(
            model_name='publication',
            name='general_comments',
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AddField(
            model_name='publication',
            name='team_comments',
            field=models.CharField(blank=True, max_length=400),
        ),
    ]
