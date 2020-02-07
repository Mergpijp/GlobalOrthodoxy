# Generated by Django 2.2.9 on 2020-02-03 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0043_auto_20200131_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='collection_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='countries_plus.Country'),
        ),
    ]