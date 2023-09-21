# Generated by Django 3.2.13 on 2023-07-25 13:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dm', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dm',
            name='default_perm_write',
        ),
        migrations.RemoveField(
            model_name='dm',
            name='name',
        ),
        migrations.AddField(
            model_name='dm',
            name='user_1',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='user_1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dm',
            name='user_2',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='user_2', to=settings.AUTH_USER_MODEL),
        ),
    ]