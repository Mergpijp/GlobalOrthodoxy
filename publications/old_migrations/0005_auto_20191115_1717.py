# Generated by Django 2.0.13 on 2019-11-15 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0004_auto_20191115_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='title_subtitle_european',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='publication',
            name='title_subtitle_transcription',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='publication',
            name='title_translation',
            field=models.CharField(max_length=300),
        ),
    ]