from django.shortcuts import render, HttpResponse, redirect, get_object_or_404

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .forms import UserCreateForm
from .models import User, Post, UserFollow


def index(request):
    return render(request, 'index.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('posts:accounts_main', username= request.user.username)
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            login(request, user)
            return redirect('posts:accounts_main', username= user.username)
    else:
        form = UserCreateForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('posts:accounts_main', username= request.user.username)
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('posts:accounts_main', username=username)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('index')


@login_required
def account_redirectto_main(request):
    return redirect('posts:accounts_main', username=request.user.username)


@login_required
def account_main(request, username):
    user = get_object_or_404(User, username=username)
    allposts = user.posts.all();
    postcount = len(allposts)
    followers = user.followers.count()
    following = UserFollow.objects.filter(followed_by=user).count()
    bio = user.bio
    profile_pic = user.profile_pic
    context = {'allposts': allposts, 'postcount': postcount, 'followers': followers, 'following': following,
               'bio': bio, 'profile_pic': profile_pic, 'username': username}

    return render(request, 'accounts/main.html', context)

@login_required
def account_edit(request, username):
    if request.user.username == username:
        pass
