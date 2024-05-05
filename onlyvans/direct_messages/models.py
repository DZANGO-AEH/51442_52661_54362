from django.db import models
from account.models import CustomUser as User
from django.utils import timezone


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} -> {self.recipient}: {self.body[:50]}'


class Thread(models.Model):
    participants = models.ManyToManyField(User)
    last_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        participant_usernames = ', '.join([p.username for p in self.participants.all()])
        return f'Thread between: {participant_usernames}'