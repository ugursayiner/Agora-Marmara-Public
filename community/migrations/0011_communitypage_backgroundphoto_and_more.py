# Generated by Django 5.0.3 on 2024-05-21 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0010_remove_postcomment_parent_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitypage',
            name='backgroundphoto',
            field=models.ImageField(blank=True, default='images/default_community_background.png', upload_to='images/'),
        ),
        migrations.AddField(
            model_name='communitypage',
            name='profilephoto',
            field=models.ImageField(blank=True, default='images/default_community_pp.png', upload_to='images/'),
        ),
    ]
