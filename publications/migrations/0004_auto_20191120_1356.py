# Generated by Django 2.0.13 on 2019-11-20 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0003_auto_20191120_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='collection_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='publication_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
