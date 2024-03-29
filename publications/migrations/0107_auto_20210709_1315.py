# Generated by Django 2.2.24 on 2021-07-09 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0106_publication_pdf_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='currency',
            field=models.CharField(choices=[('0', 'unknown'), ('1', 'EUR: Euro'), ('2', 'GBP: Pound sterling'), ('3', 'SEK: Swedish krona'), ('4', 'NLD: Dutch gulden'), ('5', 'AUS: Austrian Schiling'), ('6', 'GRM: German Mark'), ('7', 'MAL: Maltese Lira'), ('8', 'BEF: Belgian Franc'), ('9', 'GRD: Greek Drachma'), ('10', 'CYP: Cypriot Pound'), ('11', 'IRP: Irish Pound')], default='0', max_length=25),
        ),
    ]
