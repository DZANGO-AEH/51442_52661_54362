from django.db import models
from account.models import CustomUser


class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    balance = models.IntegerField(default=0)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('SUBSCRIPTION', 'Subscription'),
        ('DONATION', 'Donation'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
