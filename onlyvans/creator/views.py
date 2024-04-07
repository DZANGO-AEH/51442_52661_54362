from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import creator_required
from .forms import PostForm


@login_required(login_url='login')
@creator_required
def dashboard(request):
    return render(request, 'creator/dashboard.html')


@login_required(login_url='login')
@creator_required
def create_post(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return render(request, 'creator/dashboard.html')
    context = {'form': form}
    return render(request, 'creator/create_post.html', context)
