# Generated by Django 4.0.5 on 2022-07-11 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0007_catalogue_tech_specs'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='tech_specs',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
