# Generated by Django 5.0.3 on 2024-05-30 07:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creator', '0009_tier_unique_tier_name_per_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Like',
        ),
    ]
