import os, contextlib
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, Http404
from django.http import JsonResponse, HttpResponseBadRequest

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .forms import UserCreateForm, UserEditForm
from .models import User, Post, UserFollow

from django.core.files.base import ContentFile

from django_drf_filepond.api import store_upload, delete_stored_upload, get_stored_upload_file_data
from django_drf_filepond.models import TemporaryUpload, StoredUpload

def index(request):
    return render(request, 'index.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('posts:accounts_main', username=request.user.username)
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            login(request, user)
            return redirect('posts:accounts_main', username=user.username)
    else:
        form = UserCreateForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('posts:accounts_main', username=request.user.username)
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
        if request.method == 'POST':
            form = UserEditForm(request.POST, instance=request.user)
            data = request.POST
            try:
                filepond_ids = data.getlist('filepond')
            except KeyError:
                return HttpResponseBadRequest('Missing filepond key in form.')

            if not isinstance(filepond_ids, list):
                return HttpResponseBadRequest('Unexpected data type in form.')

            if form.is_valid():
                if len(filepond_ids) >= 1:
                    for upload_id in filepond_ids:
                        tu = TemporaryUpload.objects.get(upload_id=upload_id)
                        su = store_upload(upload_id, os.path.join(upload_id, tu.upload_name))
                        (filename, file) = get_stored_upload_file_data(su)
                        user = form.save(commit=False)
                        with contextlib.closing(file):
                            user.profile_pic.save(filename, ContentFile(file.read()))

                        delete_stored_upload(upload_id, delete_file=True)
                else:
                    form.save()
                return redirect('posts:accounts_main', username=request.user.username)
        else:
            form = UserEditForm(instance=request.user)
        return render(request, 'accounts/edit.html', {'form': form})
    else:
        raise Http404("Access Denied!")
