from django.urls import path, re_path
from django.contrib import admin

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.index, name='index'),
    path('home/', views.Home.as_view(), name='home'),
    re_path(r'^home/(?P<top>24H|7D|ALL|LIKES)/$', views.Home.as_view(), name='home-top'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('subscriptions/', views.Subscriptions.as_view(), name='subscriptions'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('like/', views.Like.as_view(), name='like'),
    path('dislike/', views.Dislike.as_view(), name='dislike'),
    path('twitch/', views.TwitchTest.as_view(), name='twitch'),
    path('signup/', views.signup, name='signup'),
    path('user/new', views.UserCreateView.as_view(), name='user-create'),
    path('switch_following', views.FollowingSwitch.as_view(), name='switch-following'),
    path('syncfollows/',views.SyncFollows.as_view(),name='sync-follows'),
    path('follow/', views.Follow.as_view(), name='follow'),
    path('unfollow/', views.Unfollow.as_view(), name='unfollow'),
]
