from django.shortcuts import render
from .forms import CustomUserCreationForm

def home(request):
    return render(request, 'account/index.html')

def register(request):
    RegisterForm = CustomUserCreationForm
    context = {'form': RegisterForm}
    return render(request, 'account/register.html', context)


def login(request):
    return render(request, 'account/login.html')

