from django.contrib import admin
from .models import User, Post, PostComment, PostLike, UserFollow
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.register(UserFollow)
admin.site.register(Post)
admin.site.register(PostLike)
admin.site.register(PostComment)
