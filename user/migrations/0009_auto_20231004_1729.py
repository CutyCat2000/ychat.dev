# Generated by Django 3.2.13 on 2023-10-04 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_user_dms'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='backup_codes',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='secret_key',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
