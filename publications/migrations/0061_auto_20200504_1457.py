# Generated by Django 2.2.10 on 2020-05-04 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0060_auto_20200420_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='files/Mon,/04/May/2020/12/57/18/+0000/'),
        ),
    ]