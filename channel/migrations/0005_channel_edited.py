# Generated by Django 3.2.13 on 2023-09-19 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0004_auto_20230719_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='edited',
            field=models.BooleanField(default=False),
        ),
    ]
