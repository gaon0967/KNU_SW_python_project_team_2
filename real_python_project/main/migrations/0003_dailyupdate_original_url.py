# Generated by Django 5.2.2 on 2025-06-10 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_dailyupdate_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyupdate',
            name='original_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
