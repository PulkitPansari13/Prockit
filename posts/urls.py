from django.urls import path, include
from . import views

app_name = 'posts'

urlpatterns = [
    path('accounts/', views.account_redirectto_main, name='accounts_main_redirect'),
    path('accounts/<str:username>/', views.account_main, name='accounts_main'),
    path('accounts/<str:username>/edit/', views.account_edit, name='accounts_edit'),
    path('accounts/<str:username>/follow/', views.accountfollowtoggle, name='accounts_follow'),
    path('posts/<str:username>/new/', views.post_create, name='post_create'),
    path('posts/<str:username>/feed/', views.feed, name='feed'),
    path('posts/<str:username>/<int:postid>/', views.post_detail, name='post_detail'),
    path('posts/<str:username>/<int:postid>/like', views.postliketoggle, name='post_like'),
    path('posts/<str:username>/<int:postid>/edit', views.post_edit, name='post_edit'),
    path('posts/<int:postid>/comment', views.post_comment, name='post_comment'),
    path('posts/<int:postid>/delete', views.post_delete, name='post_delete'),
]
