# Generated by Django 4.0.5 on 2022-06-20 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0002_rename_organization_userprofileinfo_organization_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofileinfo',
            name='verifying_token',
            field=models.CharField(default=None, max_length=64, null=True),
        ),
    ]
