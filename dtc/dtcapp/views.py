from django.shortcuts import render, redirect
from django.views import generic, View
from django.urls import reverse_lazy

from .models import User

from dtcapp.twitchtools import TwitchUser, TwitchClip, TwitchTop

from django.contrib import messages

from .forms import SignUpForm

from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_protect

# Create your views here.

def index(request):
    context = {}
    return render(request, 'dtcapp/index.html', context)

class Home(generic.TemplateView):
    template_name="dtcapp/home.html"

class Profile(generic.TemplateView):
    template_name="dtcapp/profile.html"

class Subscribe(generic.TemplateView):
    template_name="dtcapp/subscribe.html"

class UserCreateView(generic.CreateView):
    model=User
    form_class=SignUpForm
    success_url = reverse_lazy('home')

    def get(self,request):
        try:
            self.username = self.request.session['twitch_name']
            self.email = self.request.session['email']
            self.picture = self.request.session['profile_image_url']
            self.id_twitch = self.request.session['twitch_id']
            self.pictureURL = self.request.session['profile_image_url']
        
        except KeyError:
            messages.error(self.request,'Twitch connection failed.')
            return redirect('index')

    def get_initial(self):
        initial = super(UserCreateView, self).get_initial()
        initial = initial.copy()
               
        initial['username'] =  self.username
        initial['email'] = self.email
        initial['picture'] = self.picture
        initial['id_twitch']= self.id_twitch
        initial['pictureURL'] = self.pictureURL

        return initial

    def form_valid(self, form):
        #Create User ?
        #TODO:Check if id_twitch is still the same than in session
        form.instance.set_password(form.cleaned_data['password'])

        return super(UserCreateView, self).form_valid(form)
        

def signup(request):
    
    twitch_user = TwitchUser()

    if twitch_user.token is not None and twitch_user.refresh_token:
        request.session['token'] = twitch_user.token
        request.session['refresh_token'] = twitch_user.refresh_token

        request.session['twitch_name'] = twitch_user.user['display_name']
        request.session['profile_image_url'] =  twitch_user.user['profile_image_url']
        request.session['email'] = twitch_user.user['email']
        request.session['twitch_id'] = twitch_user.get_user_id()

        return redirect('user-create')
    
    messages.error(request,'Twitch connection failed.')
    return redirect('index')


def login(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        return redirect('home')
    else:
        return redirect('index')

class TwitchTest(generic.TemplateView):
    template_name="dtcapp/test-twitch.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Maybe not create TwitchUser always to get the following (because it's saved in database) 
        # only use it if user press sync button
        twitchUser = TwitchUser(self.request.session['token'],self.request.session['refresh_token'])
        followers = twitchUser.get_user_following()
        
        #print(followers)

        followers_ids = [follower['to_id'] for follower in followers['data']]
        twitchClip = TwitchClip(followers_ids)
        names_followed, pictures_followed = twitchClip.get_infos_followed()

        followers={}

        for i, flw_id in enumerate(followers_ids):
            followers[flw_id] = {}
            followers[flw_id]['name'] = names_followed[i]
            followers[flw_id]['picture'] = pictures_followed[i]

        context['followers'] = followers

        clips = twitchClip.get_clips_from_all_followed()
        print(clips)
        return context
        
