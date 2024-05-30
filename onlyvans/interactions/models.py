from django.db import models
from account.models import CustomUser
from creator.models import Post
from django.utils import timezone
from django.core.exceptions import ValidationError

class Thread(models.Model):
    """
    Represents a thread of messages between two users.

    Fields:
    - participants: A many-to-many relationship with CustomUser, indicating the participants in the thread.

    Methods:
    - __str__(): Returns a string representation of the thread, listing the usernames of the participants.
    - get_other_participant(user): Given a user, returns the other participant in the thread.
    - clean(): Validates that a thread can only have two participants.
    """
    participants = models.ManyToManyField(CustomUser, related_name='threads')

    def __str__(self):
        return f"Thread between {', '.join(participant.username for participant in self.participants.all())}"

    def get_other_participant(self, user):
        """
        Returns the other participant in the thread, given one of the participants.

        Args:
            user (CustomUser): The user for whom to find the other participant.

        Returns:
            CustomUser: The other participant in the thread.
        """
        return self.participants.exclude(id=user.id).first()

    def clean(self):
        """
        Validates that the thread can only have two participants.

        Raises:
            ValidationError: If the thread has more than two participants.
        """
        super().clean()
        if self.participants.count() > 2:
            raise ValidationError("A Thread can only have two participants.")

class Message(models.Model):
    """
    Represents a message in a thread.

    Fields:
    - thread: A foreign key to the Thread in which the message is sent.
    - sender: A foreign key to the CustomUser who sent the message.
    - body: The content of the message.
    - sent_at: The timestamp when the message was sent.

    Methods:
    - __str__(): Returns a string representation of the message, indicating the sender and the thread.
    """
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender.username} in thread {self.thread}"

class Like(models.Model):
    """
    Represents a like on a post by a user.

    Fields:
    - user: A foreign key to the CustomUser who liked the post.
    - post: A foreign key to the Post that was liked.
    - liked_at: The timestamp when the post was liked.

    Meta:
    - unique_together: Ensures that a user can like a post only once.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    """
    Represents a comment on a post by a user.

    Fields:
    - user: A foreign key to the CustomUser who made the comment.
    - post: A foreign key to the Post that was commented on.
    - text: The content of the comment.
    - commented_at: The timestamp when the comment was made.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)
