from django.db import models
from django.contrib.auth.models import AbstractUser
from random import randint
# Create your models here.


class User(AbstractUser):
    bio = models.TextField(max_length=250, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics', default='default_profile_pic' + str(randint(1,10)) + '.svg')
    followers = models.ManyToManyField('self', through="UserFollow")


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
    file1 = models.FileField(upload_to='posts/files', null=False)
    file2 = models.FileField(upload_to='posts/files', null=True)
    file3 = models.FileField(upload_to='posts/files', null=True)

    def total_likes(self):
        return self.likers.count()

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