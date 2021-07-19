# Generated by Django 2.2.24 on 2021-07-12 14:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0108_auto_20210712_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='church',
            name='authors',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author_churches_list', to='publications.Author'),
        ),
    ]