from django.shortcuts import render, redirect
from django.views import generic, View


from dtcapp.twitchtools import TwitchUser, TwitchClip, TwitchTop

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

        followers_ids = [follower['to_id'] for follower in followers['data']]
        twitchClip = TwitchClip(followers_ids)
        clips = twitchClip.get_clips_from_all_followed()
        print(clips)
        return context
        