# Generated by Django 4.0.5 on 2022-06-20 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_alter_userprofileinfo_verifying_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofileinfo',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
    ]
