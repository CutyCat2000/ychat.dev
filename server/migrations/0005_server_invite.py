# Generated by Django 3.2.13 on 2023-07-25 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_server_channels'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='invite',
            field=models.CharField(default='', max_length=25),
        ),
    ]
