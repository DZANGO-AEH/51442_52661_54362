from django.core.management.base import BaseCommand
from client.tasks import renew_subscriptions

class Command(BaseCommand):
    help = 'Renew subscriptions that are due for renewal'

    def handle(self, *args, **kwargs):
        renew_subscriptions()
        self.stdout.write(self.style.SUCCESS('Successfully renewed subscriptions'))
