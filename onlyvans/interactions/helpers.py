from client.models import Subscription


def has_messaging_permission(sender, recipient):
    """
    Determine if two users have messaging permissions.
    """
    # Creator to follower
    creator_to_follower = Subscription.objects.filter(
        user=recipient,
        tier__user=sender,
        tier__message_permission=True,
        status='ACTIVE'
    ).exists()

    # Follower to creator
    follower_to_creator = Subscription.objects.filter(
        user=sender,
        tier__user=recipient,
        tier__message_permission=True,
        status='ACTIVE'
    ).exists()

    return creator_to_follower or follower_to_creator