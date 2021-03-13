from django.shortcuts import render, redirect
from django.views import generic, View


from dtcapp.twitchtools import TwitchUser

# Create your views here.
class LogIn(View):
    def get(self, request):
        twitchUser = TwitchUser()
        request.session['token'] = twitchUser.token
        request.session['refresh_token'] = twitchUser.refresh_token
        return redirect('twitch')

class TwitchTest(generic.TemplateView):
    template_name="dtcapp/test-twitch.html"

    def get_context_data(self, **kwargs):
        twitchUser = TwitchUser(self.request.session['token'],self.request.session['refresh_token'])
        followers = twitchUser.get_user_following()
        context = super().get_context_data(**kwargs)
        context['followers'] = followers['data']
        print(followers)
        return context
        