# Generated by Django 2.0.13 on 2019-11-20 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0004_auto_20191120_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='nr_of_pages',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
