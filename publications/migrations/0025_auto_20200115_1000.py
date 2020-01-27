# Generated by Django 2.2.8 on 2020-01-15 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0024_auto_20200110_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255)),
                ('files', models.FileField(blank=True, null=True, upload_to='files')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='publication',
            name='contact_info',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='documents',
        ),
        migrations.AddField(
            model_name='publication',
            name='contact_email',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='publication',
            name='contact_telephone_number',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='publication',
            name='contact_website',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.DeleteModel(
            name='Document',
        ),
        migrations.AddField(
            model_name='publication',
            name='uploadedfiles',
            field=models.ManyToManyField(blank=True, null=True, to='publications.UploadedFile'),
        ),
    ]