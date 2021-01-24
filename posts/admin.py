from django.contrib import admin
from .models import User, Post, PostComment, PostLike, UserFollow
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(User, UserAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'description', 'created_at', 'modified_at')


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user')


class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'text', 'commented_at')


admin.site.register(UserFollow)
admin.site.register(Post, PostAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(PostComment, PostCommentAdmin)
