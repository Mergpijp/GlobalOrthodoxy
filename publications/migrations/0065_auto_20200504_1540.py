# Generated by Django 2.2.10 on 2020-05-04 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0064_auto_20200504_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='files/%Y/%m/%d/%H/%M/%S/%f/'),
        ),
    ]