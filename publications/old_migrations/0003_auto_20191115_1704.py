# Generated by Django 2.0.13 on 2019-11-15 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0002_auto_20191115_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='published_by',
            field=models.CharField(default='default', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='publication',
            name='printed_by',
            field=models.CharField(max_length=100),
        ),
    ]
