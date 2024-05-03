# Generated by Django 5.0.3 on 2024-04-08 19:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creator', '0002_alter_post_tier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='tier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tier_media', to='creator.tier'),
        ),
    ]