import os, contextlib
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, Http404
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .forms import UserCreateForm, UserEditForm, PostForm
from .models import User, Post, UserFollow, PostComment

from django.core.files.base import ContentFile

from django_drf_filepond.api import store_upload, delete_stored_upload, get_stored_upload_file_data
from django_drf_filepond.models import TemporaryUpload, StoredUpload


def index(request):
    if request.user.is_authenticated:
        return redirect('posts:feed', username=request.user.username)
    return render(request, 'index.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('posts:accounts_main', username=request.user.username)
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.save()
            login(request, user,backend='django.contrib.auth.backends.ModelBackend')
            return redirect('posts:accounts_main', username=user.username)
    else:
        form = UserCreateForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('posts:accounts_main', username=request.user.username)
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user,backend='django.contrib.auth.backends.ModelBackend')
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
    obj = UserFollow.objects.filter(account=user, followed_by=request.user)
    if len(obj):
        isfollowing = True
    else:
        isfollowing = False
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
                        user.profile_pic.delete(False)
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


@login_required
def accountfollowtoggle(request, username):
    if request.method == 'GET':
        acc = get_object_or_404(User, username=username)
        data = {}
        updated = False
        followed = False
        if request.user.is_authenticated:
            if request.user in acc.followers.all():
                acc.followers.remove(request.user)
            else:
                acc.followers.add(request.user)
                followed = True
            updated = True
        data['updated'] = updated
        data['followed'] = followed
        return JsonResponse(data)


@login_required
def post_create(request, username):
    if request.user.username == username:
        if request.method == 'POST':
            data = request.POST
            try:
                filepond_ids = data.getlist('filepond')
            except KeyError:
                return HttpResponseBadRequest('Missing filepond key in form.')

            if not isinstance(filepond_ids, list):
                return HttpResponseBadRequest('Unexpected data type in form.')
            filecount = len(filepond_ids)
            form = PostForm(request.POST, filecount=filecount)
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                for i in range(len(filepond_ids)):
                    upload_id = filepond_ids[i]
                    tu = TemporaryUpload.objects.get(upload_id=upload_id)
                    su = store_upload(upload_id, os.path.join(upload_id, tu.upload_name))
                    (filename, file) = get_stored_upload_file_data(su)

                    if i == 0:
                        with contextlib.closing(file):
                            post.file1.save(filename, ContentFile(file.read()))
                    elif i == 1:
                        with contextlib.closing(file):
                            post.file2.save(filename, ContentFile(file.read()))
                    elif i == 2:
                        with contextlib.closing(file):
                            post.file3.save(filename, ContentFile(file.read()))

                    delete_stored_upload(upload_id, delete_file=True)

                return redirect('posts:accounts_main', username=request.user.username)
        else:
            form = PostForm(filecount=0)
        return render(request, 'post/post_create.html', {'form': form})
    else:
        raise Http404("Access Denied!")


@login_required
def post_edit(request, username, postid):
    if request.user.username == username:
        context = {}
        if request.method == 'POST':
            data = request.POST
            try:
                filepond_ids = data.getlist('filepond')
            except KeyError:
                return HttpResponseBadRequest('Missing filepond key in form.')

            if not isinstance(filepond_ids, list):
                return HttpResponseBadRequest('Unexpected data type in form.')
            filecount = len(filepond_ids)
            post = get_object_or_404(Post, pk=postid, user=request.user)
            form = PostForm(request.POST, filecount=filecount, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                if filecount < 3 and post.file3 is not None and post.file3 != '':
                    post.file3.delete(False)
                    if filecount == 1 and post.file2 is not None and post.file2 != '':
                        post.file2.delete()
                for i in range(len(filepond_ids)):
                    upload_id = filepond_ids[i]
                    tu = TemporaryUpload.objects.get(upload_id=upload_id)
                    su = store_upload(upload_id, os.path.join(upload_id, tu.upload_name))
                    (filename, file) = get_stored_upload_file_data(su)

                    if i == 0:
                        with contextlib.closing(file):
                            post.file1.save(filename, ContentFile(file.read()))
                    elif i == 1:
                        with contextlib.closing(file):
                            post.file2.save(filename, ContentFile(file.read()))
                    elif i == 2:
                        with contextlib.closing(file):
                            post.file3.save(filename, ContentFile(file.read()))

                    delete_stored_upload(upload_id, delete_file=True)

                return redirect('posts:accounts_main', username=request.user.username)
        else:
            post = get_object_or_404(Post, pk=postid, user=request.user)
            form = PostForm(filecount=0, instance=post)
            posturls = []
            if post.filetype1() is not None:
                posturls.append(post.file1.url)
            if post.filetype2() is not None:
                posturls.append(post.file2.url)
            if post.filetype3() is not None:
                posturls.append(post.file3.url)
            context['posturls'] = posturls
        context['form'] = form
        return render(request, 'post/post_edit.html', context)
    else:
        raise Http404("Access Denied!")


@login_required
def post_detail(request, username, postid):
    if request.method == "GET":
        owner = get_object_or_404(User, username=username)
        post = get_object_or_404(Post, pk=postid, user=owner)
        isowner = request.user.username == username
        comments = post.comments.all()
        context = {'owner': owner, 'post': post, 'isowner': isowner, 'comments': comments}
        return render(request, 'post/post_detail.html', context)


@login_required
def post_delete(request, postid):
    if request.method == 'GET':
        post = get_object_or_404(Post, user=request.user, pk=postid)
        post.delete()
        return redirect('posts:accounts_main', username=request.user.username)
    else:
        raise Http404("Access Denied!")


@login_required
def postliketoggle(request, **kwargs):
    if request.method == "GET":
        pk = kwargs['postid']
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        data = post.like_toggle(user)
        return JsonResponse(data)


@login_required
def post_comment(request, postid):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=postid)
        text = request.POST.get('comment', '')
        data = {}
        if text != '':
            comment = PostComment(user=request.user, post=post, text=text)
            comment.save()
            data['success'] = True
            data['profile_pic'] = request.user.profile_pic.url
            data['text'] = text
            data['commented_at'] = comment.commented_at
            return JsonResponse(data)
        data['success'] = False
        return JsonResponse(data)


@login_required
def feed(request, username):
    if request.user.username == username:
        if request.method == 'GET':
            user = request.user
            following = user.user_set.values_list('id', flat=True)
            followinglist = list(following)
            if followinglist:
                posts = Post.objects.filter(user__id__in=followinglist)
                if not posts:
                    posts = Post.objects.all()[:10]
            else:
                posts = Post.objects.all()[:10]
            followrecommend = User.objects.exclude(Q(id__in=followinglist) | Q(username=username))[:10]
            context = {'posts': posts, 'recommendation': followrecommend}
            return render(request, 'feed.html', context)

    else:
        raise Http404("Access Denied!")
