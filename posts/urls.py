from django.urls import path, include
from . import views

app_name = 'posts'

urlpatterns = [
    path('accounts/', views.account_redirectto_main, name='accounts_main_redirect'),
    path('accounts/<str:username>/', views.account_main, name='accounts_main'),
    path('accounts/<str:username>/edit', views.account_edit, name='accounts_edit'),
]