# Generated by Django 5.1.6 on 2025-03-31 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0003_postimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
        migrations.AddField(
            model_name='postimage',
            name='thumbnail',
            field=models.ImageField(blank=True, upload_to='post_thumbnails'),
        ),
    ]
