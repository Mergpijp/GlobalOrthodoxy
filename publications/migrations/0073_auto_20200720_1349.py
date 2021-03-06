# Generated by Django 2.2.13 on 2020-07-20 11:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0072_auto_20200717_1445'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='imagecontent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='imagecontent', to='publications.ImageContent'),
        ),
    ]
