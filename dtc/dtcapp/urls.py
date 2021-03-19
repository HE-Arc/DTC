from django.urls import path
from django.contrib import admin

from . import views

# TODO-ADV-1-3 Uncomment thos four lines used by restframework
#from rest_framework import routers
#router = routers.DefaultRouter()
#router.register('users', views.UserViewSet)
#router.register('soldiers', views.SoldierViewSet)


urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('home/', views.Home.as_view(), name='home'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('logging_in/', views.LoggingIn.as_view(), name='logging_in'),
    path('subscribe/', views.Subscribe.as_view(), name='subscribe'),
    path('login/',views.login, name='login'),
    path('twitch/',views.TwitchTest.as_view(),name='twitch'),
    path('signup/',views.signup,name='signup'),
    path('user/new',views.UserCreateView.as_view(),name='user-create')
]
    
    
    
    