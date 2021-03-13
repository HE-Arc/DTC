from django.urls import path
from django.contrib import admin

from . import views

# TODO-ADV-1-3 Uncomment thos four lines used by restframework
#from rest_framework import routers
#router = routers.DefaultRouter()
#router.register('users', views.UserViewSet)
#router.register('soldiers', views.SoldierViewSet)


urlpatterns = [
    path('login/',views.LogIn.as_view(), name='login'),
    path('twitch/',views.TwitchTest.as_view(),name='twitch')
]
    
    
    
    