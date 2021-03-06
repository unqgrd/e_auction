# Generated by Django 4.0.5 on 2022-06-23 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_alter_catalogue_starting_bid'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogueFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.FileField(blank=True, null=True, upload_to='catalogue_file')),
                ('catalogue_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.catalogue')),
            ],
        ),
    ]
