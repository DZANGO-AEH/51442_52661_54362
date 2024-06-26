# Generated by Django 5.0.3 on 2024-05-30 14:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('creator', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('CANCELLED', 'Cancelled'), ('EXPIRED', 'Expired')], default='ACTIVE', max_length=10)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField()),
                ('tier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to='creator.tier')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'ACTIVE')), fields=('user', 'tier'), name='unique_active_subscription_to_tier'),
        ),
    ]
