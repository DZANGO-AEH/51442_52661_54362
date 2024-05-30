from client.models import Subscription


def has_messaging_permission(sender, recipient):
    """
    Checks if there is messaging permission between the sender and recipient.

    There are two conditions under which messaging permission is granted:
    1. The recipient has an active subscription to one of the sender's tiers that allows messaging.
    2. The sender has an active subscription to one of the recipient's tiers that allows messaging.

    Args:
        sender (CustomUser): The user sending the message.
        recipient (CustomUser): The user receiving the message.

    Returns:
        bool: True if there is messaging permission between the sender and recipient, False otherwise.
    """

    # Check if the recipient has an active subscription to the sender's tier with messaging permission
    creator_to_follower = Subscription.objects.filter(
        user=recipient,
        tier__user=sender,
        tier__message_permission=True,
        status='ACTIVE'
    ).exists()

    # Check if the sender has an active subscription to the recipient's tier with messaging permission
    follower_to_creator = Subscription.objects.filter(
        user=sender,
        tier__user=recipient,
        tier__message_permission=True,
        status='ACTIVE'
    ).exists()

    # Return True if either condition is met, otherwise False
    return creator_to_follower or follower_to_creator
