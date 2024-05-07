from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.models import CustomUser as User
from .forms import MessageForm
from .models import Message, Thread
from creator.models import Subscription
from django.db.models import Count, Q, Max
from django.http import Http404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.exceptions import PermissionDenied


@login_required
def direct_messages(request):
    user = request.user
    threads = Thread.objects.filter(participants=user).annotate(
        last_message_date=Max('messages__sent_at')
    ).order_by('-last_message_date')

    threads_context = [
        {
            'thread': thread,
            'other_participant': thread.get_other_participant(user),
        }
        for thread in threads if has_messaging_permission(user, thread.get_other_participant(user))
    ]

    return render(request, 'direct_messages/threads.html', {
        'threads': threads_context,
    })


@login_required
def view_thread(request, username=None, thread_id=None):
    user = request.user

    if username:
        other_user = get_object_or_404(User, username=username)

        # Prevent users from messaging themselves
        if user == other_user:
            raise Http404("You cannot send a message to yourself.")

        thread = Thread.objects.filter(participants=user).filter(participants=other_user).first()
        if not thread:
            # Prevent more than two participants in a thread
            if Thread.objects.filter(participants=user).count() >= 2:
                raise ValidationError("A Thread can only have two participants.")
            thread = Thread.objects.create()
            thread.participants.add(user, other_user)
    else:
        thread = get_object_or_404(Thread, id=thread_id)
        if user not in thread.participants.all():
            raise Http404("You are not a participant in this thread.")

        other_user = thread.get_other_participant(user)

    # Messaging permissions check
    if not has_messaging_permission(user, other_user):
        raise PermissionDenied("You do not have permission to message this user.")

    form = MessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        message = form.save(commit=False)
        message.sender = user
        message.thread = thread
        message.save()
        return redirect('direct_messages:view_thread', thread_id=thread.id)

    return render(request, 'direct_messages/view_thread.html', {
        'thread': thread,
        'messages': thread.messages.order_by('sent_at'),
        'form': form,
        'other_participant': other_user,
    })


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
