import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from random import randint
# Create your models here.


class User(AbstractUser):
    bio = models.TextField(max_length=250, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics', default='default_profile_pic' + str(randint(1,10)) + '.svg')
    followers = models.ManyToManyField('self', through="UserFollow", symmetrical=False)


class UserFollow(models.Model):
    account = models.ForeignKey(User, related_name='followed_by', on_delete=models.CASCADE)
    followed_by = models.ForeignKey(User, related_name='follows', on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add =True)

    class Meta:
        unique_together = ["account", "followed_by"]


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=250, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    code_link = models.URLField(blank=True, null=True)
    likers = models.ManyToManyField(User, through='PostLike')
    file1 = models.FileField(upload_to='posts/files', null=False, blank=False)
    file2 = models.FileField(upload_to='posts/files', null=True, blank=True)
    file3 = models.FileField(upload_to='posts/files', null=True, blank=True)

    def like_toggle(self, requser):
        data = {}
        updated = False
        liked = False
        if requser.is_authenticated:
            if requser in self.likers.all():
                self.likers.remove(requser)
            else:
                self.likers.add(requser)
                liked = True
            updated = True
        data['liked'] = liked
        data['updated'] = updated
        return data

    def total_likes(self):
        return self.likers.count()

    def total_comments(self):
        return self.comments.count()

    def filetype1(self):
        if self.file1 is not None and self.file1 != '':
            name, extension = os.path.splitext(self.file1.name)
            extension = extension.lstrip('.')
            video_extentions = ['mp4', 'mov', 'mkv', 'ogg', 'webm', 'wmv', 'mpeg']
            img_extention = ['apng', 'png', 'avif', 'gif', 'jpg', 'jpeg', 'jfif', 'svg', 'webp']
            if extension in video_extentions:
                return 'video'
            elif extension in img_extention:
                return 'img'
            else:
                return None
        else:
            return None

    def filetype2(self):
        if self.file2 is not None and self.file2 != '':
            name, extension = os.path.splitext(self.file2.name)
            extension = extension.lstrip('.')
            video_extentions = ['mp4', 'mov', 'mkv', 'ogg', 'webm', 'wmv', 'mpeg']
            img_extention = ['apng', 'png', 'avif', 'gif', 'jpg', 'jpeg', 'jfif', 'svg', 'webp']
            if extension in video_extentions:
                return 'video'
            elif extension in img_extention:
                return 'img'
            else:
                return None
        else:
            return None

    def filetype3(self):
        if self.file3 is not None and self.file3 != '':
            name, extension = os.path.splitext(self.file3.name)
            extension = extension.lstrip('.')
            video_extentions = ['mp4', 'mov', 'mkv', 'ogg', 'webm', 'wmv', 'mpeg']
            img_extention = ['apng', 'png', 'avif', 'gif', 'jpg', 'jpeg', 'jfif', 'svg', 'webp']
            if extension in video_extentions:
                return 'video'
            elif extension in img_extention:
                return 'img'
            else:
                return None
        else:
            return None

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts')

    def __str__(self):
        return 'Post --> {} by User --> {}'.format(self.post.title, self.user.username)

    class Meta:
        unique_together = ['post', 'user']


class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False)
    commented_at = models.DateTimeField(auto_now_add =True)

    class Meta:
        ordering = ['-commented_at']