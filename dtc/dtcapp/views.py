from django.shortcuts import render, redirect
from django.views import generic, View
from django.urls import reverse_lazy

from .models import User

from dtcapp.twitchtools import TwitchUser, TwitchClip, TwitchTop

from django.contrib import messages

from .forms import SignUpForm

from django.contrib.auth import login as loginto
from django.contrib.auth import logout as logoutof
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_protect

# Create your views here.

def index(request):
    context = {}

    # Cannot access the main index page if authenticated already
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return render(request, 'dtcapp/index.html', context)
    
class AuthView(generic.TemplateView):
    """A base View class inheriting from TemplateView to allow access only when authenticated."""

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('logging_in')
        return super(AuthView, self).get(request, *args, **kwargs)

class NotAuthView(generic.TemplateView):
    """A base View class inheriting from TemplateView to allow access only when NOT authenticated."""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super(NotAuthView, self).get(request, *args, **kwargs)

class Home(AuthView):
    template_name = "dtcapp/home.html"


class Profile(AuthView):
    template_name = "dtcapp/profile.html"


class Subscribe(generic.TemplateView):
    template_name = "dtcapp/subscribe.html"


class LoggingIn(NotAuthView):
    template_name = "dtcapp/logging_in.html"


class UserCreateView(generic.CreateView):
    model = User
    form_class = SignUpForm
    success_url = reverse_lazy('home')

    def get(self,request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        try:
            self.username = self.request.session['twitch_name']
            self.email = self.request.session['email']
            self.picture = self.request.session['profile_image_url']
            self.id_twitch = self.request.session['twitch_id']
            self.pictureURL = self.request.session['profile_image_url']
        
        except KeyError:
            messages.error(self.request,'Twitch connection failed.')
            return redirect('index')
        
        return super(UserCreateView, self).get(request, *args, **kwargs)

    def get_initial(self):
        initial = super(UserCreateView, self).get_initial()
        initial = initial.copy()

        self.username = self.request.session['twitch_name']
        self.email = self.request.session['email']
        self.picture = self.request.session['profile_image_url']
        self.id_twitch = self.request.session['twitch_id']
        self.pictureURL = self.request.session['profile_image_url']

        initial['username'] =  self.username  
        initial['email'] = self.email
        initial['picture'] = self.picture
        initial['id_twitch']= self.id_twitch
        initial['pictureURL'] = self.pictureURL

        return initial

    def form_valid(self, form):
        #Create User ?
        #TODO:Check if id_twitch is still the same than in session

        if form.cleaned_data['id_twitch'] == self.id_twitch:  
            form.instance.set_password(form.cleaned_data['password'])

            user = form.save(commit=False)

            user.save()

            user.update_follows(self.request.session['followers_ids'])

            loginto(self.request, user)

            return super(UserCreateView, self).form_valid(form)
        else:
            messages.error(self.request,'ID Twitch has been changed.')
            return redirect('user-create')
        

def signup(request):

    # Cannot signup if already authenticated
    if request.user.is_authenticated:
        return redirect('home')

    twitch_user = TwitchUser()

    if twitch_user.token is not None and twitch_user.refresh_token:
        request.session['token'] = twitch_user.token
        request.session['refresh_token'] = twitch_user.refresh_token

        request.session['twitch_name'] = twitch_user.user['display_name']
        request.session['profile_image_url'] = twitch_user.user['profile_image_url']
        request.session['email'] = twitch_user.user['email']
        request.session['twitch_id'] = twitch_user.get_user_id()

        followers = twitch_user.get_user_following()
        followers_ids = [follower['to_id'] for follower in followers['data']]
        request.session['followers_ids'] = followers_ids

        return redirect('user-create')
    
    messages.error(request,'Twitch connection failed.')
    return redirect('index')


def login(request):
    user = authenticate(
        username=request.POST['username'], password=request.POST['password'])

    if user is not None:
        loginto(request, user)
        return redirect('home')
    else:
        return redirect('index')


def logout(request):

    if request.user.is_authenticated:
        logoutof(request)
    
    return redirect('index')

class TwitchTest(AuthView):
    template_name = "dtcapp/test-twitch.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Maybe not create TwitchUser always to get the following (because it's saved in database)
        # only use it if user press sync button
        twitchUser = TwitchUser(
            self.request.session['token'], self.request.session['refresh_token'])
        followers = twitchUser.get_user_following()

        # print(followers)

        followers_ids = [follower['to_id'] for follower in followers['data']]
        twitchClip = TwitchClip(followers_ids)
        names_followed, pictures_followed = twitchClip.get_infos_followed()

        followers = {}

        for i, flw_id in enumerate(followers_ids):
            followers[flw_id] = {}
            followers[flw_id]['name'] = names_followed[i]
            followers[flw_id]['picture'] = pictures_followed[i]

        context['followers'] = followers

        clips = twitchClip.get_clips_from_all_followed()
        print(clips)
        return context
