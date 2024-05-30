from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MessageForm
from account.models import CustomUser as User
from .models import Thread
from creator.models import Post
from interactions.models import Like
from  .helpers import has_messaging_permission
from django.db.models import Max
from django.core.paginator import Paginator
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse


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

    paginator = Paginator(threads_context, 20)
    page_number = request.GET.get('page')
    threads_page = paginator.get_page(page_number)

    return render(request, 'direct_messages/threads.html', {
        'threads': threads_page,
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
            # Create a new thread
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
        return redirect('view_thread', thread_id=thread.id)

    return render(request, 'direct_messages/view_thread.html', {
        'thread': thread,
        'direct_messages': thread.messages.order_by('sent_at'),
        'form': form,
        'other_participant': other_user,
    })

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        like.save()
        liked = True

    return JsonResponse({'success': True, 'likes_count': post.likes_count, 'liked': liked})




