# Generated by Django 5.0.3 on 2024-05-04 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='paypal_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='PayPal email'),
        ),
    ]