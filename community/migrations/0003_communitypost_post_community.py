# Generated by Django 5.0.3 on 2024-04-20 17:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_communitypost'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitypost',
            name='post_community',
            field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.CASCADE, to='community.communitypage'),
        ),
    ]
