from django.shortcuts import render, redirect
from django.views import generic, View


from dtcapp.twitchtools import TwitchUser

# Create your views here.
class LogIn(View):
    def get(self, request):
        twitchUser = TwitchUser()
        request.session['token'] = twitchUser.token
        request.session['twitchUser'] = twitchUser
        return redirect('twitch')

class TwitchTest(generic.TemplateView):
    template_name="dtcapp/test-twitch.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['followers'] = self.followers
        return context
        
    def get(self,request):
        twitchUser = request.session['twitchUser']
        self.followers = twitchUser.get_user_following()