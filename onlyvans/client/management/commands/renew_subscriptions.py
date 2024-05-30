from django.core.management.base import BaseCommand
from client.tasks import renew_subscriptions


class Command(BaseCommand):
    """
    Custom management command to renew subscriptions that are due for renewal.

    This command can be run using Django's management command system. It calls
    the `renew_subscriptions` function to renew any subscriptions that are
    due for renewal and outputs a success message upon completion.
    """
    help = 'Renew subscriptions that are due for renewal'

    def handle(self, *args, **kwargs):
        """
        The entry point for the command. Calls the `renew_subscriptions` function
        and writes a success message to stdout.
        """
        renew_subscriptions()
        self.stdout.write(self.style.SUCCESS('Successfully renewed subscriptions'))
