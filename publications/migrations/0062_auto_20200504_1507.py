# Generated by Django 2.2.10 on 2020-05-04 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0061_auto_20200504_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='files/2020/05/04/15/07/00/'),
        ),
    ]