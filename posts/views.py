from django.shortcuts import render, HttpResponse, redirect

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .forms import UserCreateForm


# Create your views here.


def index(request):
    return render(request, 'index.html')


def user_logout(request):
    logout(request)
    return redirect('index')


def signup(request):
    if request.user.is_authenticated:
        return HttpResponse('<h1>Already Logged in</h1>')
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            login(request, user)
            return HttpResponse('<h1>Logged in</h1>')
    else:
        form = UserCreateForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(request = request, data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
