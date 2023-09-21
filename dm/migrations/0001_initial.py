# Generated by Django 3.2.13 on 2023-07-25 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('message', '0002_message_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='DM',
            fields=[
                ('name', models.CharField(max_length=12)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('default_perm_write', models.BooleanField(default=True)),
                ('messages', models.ManyToManyField(related_name='dm_messages', to='message.Message')),
            ],
        ),
    ]
