from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from account.models import CustomUser as User
from .forms import MessageForm
from creator.models import Subscription
from .models import Message, Thread
from django.db.models import Q

@login_required
def message_threads(request):
    user = request.user
    threads = Thread.objects.filter(participants=user).order_by('-last_message__timestamp')
    return render(request, 'direct_messages/threads.html', {'threads': threads})

@login_required
def send_message(request, username):
    user = request.user
    recipient = get_object_or_404(User, username=username)

    if not has_messaging_permission(user, recipient):
        return render(request, 'direct_messages/no_permission.html', {'user': user})

    form = MessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        thread = Thread.objects.filter(
            Q(participants=user) & Q(participants=recipient)
        ).first()
        if not thread:
            thread = Thread.objects.create()
            thread.participants.add(user, recipient)

        message = form.save(commit=False)
        message.sender = user
        message.recipient = recipient
        message.save()

        thread.last_message = message
        thread.save()
        return redirect('direct_messages:view_thread', thread_id=thread.id)

    return render(request, 'direct_messages/send_message.html', {'recipient': recipient, 'form': form})

@login_required
def view_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    user = request.user
    form = MessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        message = form.save(commit=False)
        message.sender = user
        message.recipient = thread.get_other_participant(user)
        message.save()
        thread.last_message = message
        thread.save()
        return redirect('direct_messages:view_thread', thread_id=thread.id)

    return render(request, 'direct_messages/view_thread.html', {'thread': thread, 'form': form})
def has_messaging_permission(sender, recipient):
    if sender.is_content_creator:
        # Creator to follower
        return Subscription.objects.filter(user=recipient, tier__user=sender, tier__message_permission=True, status='ACTIVE').exists()
    else:
        # Follower to creator
        return Subscription.objects.filter(user=sender, tier__user=recipient, tier__message_permission=True, status='ACTIVE').exists()