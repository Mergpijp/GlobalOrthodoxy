# Generated by Django 2.2.9 on 2020-01-24 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0027_auto_20200115_1232'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uploadedfile',
            old_name='files',
            new_name='file',
        ),
    ]