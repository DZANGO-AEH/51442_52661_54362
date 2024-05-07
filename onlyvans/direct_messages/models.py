from django.db import models
from account.models import CustomUser as User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Thread(models.Model):
    participants = models.ManyToManyField(User, related_name='threads')

    def __str__(self):
        return f"Thread between {', '.join(participant.username for participant in self.participants.all())}"

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

    def clean(self):
        super().clean()
        if self.participants.count() > 2:
            raise ValidationError("A Thread can only have two participants.")

class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender.username} in thread {self.thread}"

