from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MessageForm
from account.models import CustomUser
from .models import Thread
from creator.models import Post
from interactions.models import Like
from .helpers import has_messaging_permission
from django.db.models import Max
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages

@login_required
def direct_messages(request):
    """
    Display the direct messages for the logged-in user.

    This view retrieves all message threads involving the logged-in user,
    annotates them with the date of the last message, and orders them by
    this date. Threads are paginated with 20 threads per page.

    Only threads where the user has messaging permission with the other
    participant are included in the context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered direct messages page with threads.
    """
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
    """
    View and send messages in a specific thread.

    If `username` is provided, a thread between the logged-in user and
    the specified user is retrieved or created. If `thread_id` is provided,
    the specific thread is retrieved.

    Messaging permissions are checked before displaying or sending messages.

    Args:
        request (HttpRequest): The HTTP request object.
        username (str, optional): The username of the other participant.
        thread_id (int, optional): The ID of the thread.

    Returns:
        HttpResponse: The rendered view thread page with messages and form.
    """
    user = request.user

    if username:
        other_user = get_object_or_404(CustomUser, username=username)

        # Prevent users from messaging themselves
        if user == other_user:
            messages.error(request, "You cannot message yourself.")
            return redirect('direct_messages')

        thread = Thread.objects.filter(participants=user).filter(participants=other_user).first()
        if not thread:
            # Create a new thread
            thread = Thread.objects.create()
            thread.participants.add(user, other_user)
    else:
        thread = get_object_or_404(Thread, id=thread_id)
        if user not in thread.participants.all():
            messages.error(request, "You do not have permission to view this thread.")
            return redirect('direct_messages')

        other_user = thread.get_other_participant(user)

    # Messaging permissions check
    if not has_messaging_permission(user, other_user):
        messages.error(request, "You do not have permission to message this user.")
        return redirect('direct_messages')

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
    """
    Like or unlike a specific post.

    If the post is already liked by the user, the like is removed.
    Otherwise, a new like is added. The view returns a JSON response
    indicating the success status, the current number of likes, and
    whether the post is now liked by the user.

    Args:
        request (HttpRequest): The HTTP request object.
        post_id (int): The ID of the post to be liked or unliked.

    Returns:
        JsonResponse: A JSON response with the success status, likes count, and liked status.
    """
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        like.save()
        liked = True

    return JsonResponse({'success': True, 'likes_count': post.likes_count, 'liked': liked})
