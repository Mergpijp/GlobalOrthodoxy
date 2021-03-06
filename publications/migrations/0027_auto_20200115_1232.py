# Generated by Django 2.2.8 on 2020-01-15 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0026_auto_20200115_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormOfPublication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='publication',
            name='form_of_publication',
        ),
        migrations.AddField(
            model_name='publication',
            name='form_of_publication',
            field=models.ManyToManyField(to='publications.FormOfPublication'),
        ),
    ]
