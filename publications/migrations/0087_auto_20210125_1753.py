# Generated by Django 2.2.13 on 2021-01-25 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0086_publication_is_stub'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publication',
            old_name='author',
            new_name='authors',
        ),
        migrations.RenameField(
            model_name='publication',
            old_name='translator',
            new_name='translators',
        ),
    ]