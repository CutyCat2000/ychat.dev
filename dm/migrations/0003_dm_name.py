# Generated by Django 3.2.13 on 2023-07-25 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dm', '0002_auto_20230725_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='dm',
            name='name',
            field=models.CharField(default='', max_length=50),
        ),
    ]
