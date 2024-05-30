from django.db import models
from account.models import CustomUser


class Wallet(models.Model):
    """
    Model representing a user's wallet.

    Fields:
        user (OneToOneField): The user to whom this wallet belongs. Deletes the wallet if the user is deleted.
        balance (IntegerField): The current balance of points in the wallet. Defaults to 0.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    balance = models.IntegerField(default=0)


class Transaction(models.Model):
    """
    Model representing a transaction made by a user.

    Fields:
        user (ForeignKey): The user who made the transaction. Deletes transactions if the user is deleted.
        type (CharField): The type of the transaction. Choices are 'PURCHASE', 'SUBSCRIPTION', 'DONATION', 'WITHDRAWAL'.
        amount (DecimalField): The amount of the transaction, allowing for up to 10 digits with 2 decimal places.
        timestamp (DateTimeField): The time when the transaction was made. Automatically set to the current date and time when the transaction is created.
        description (TextField): A description of the transaction. Can be blank or null.
    """
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
