# Generated by Django 5.0.3 on 2024-05-23 18:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exam',
            old_name='community',
            new_name='exam_community',
        ),
    ]
