from django.shortcuts import render, redirect
from django.views import generic, View
from django.urls import reverse_lazy

from .models import User, Following

from dtcapp.twitchtools import TwitchUser, TwitchClip, TwitchTop, TwitchToken

from django.contrib import messages

from .forms import SignUpForm

from django.contrib.auth import login as log_into
from django.contrib.auth import logout as logout_of
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_protect


from django.db.models import F

# Create your views here.


class AuthView(generic.TemplateView):
    """A base View class inheriting from TemplateView to allow access only when authenticated."""

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super(AuthView, self).get(request, *args, **kwargs)


class NotAuthView(generic.TemplateView):
    """A base View class inheriting from TemplateView to allow access only when NOT authenticated."""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super(NotAuthView, self).get(request, *args, **kwargs)


# Views

def index(request):

    # Cannot access the main index page if authenticated already
    if request.user.is_authenticated:
        return redirect('home')
    else:
        context = {}
        id, link = TwitchToken.get_link()
        if id is None:
            context['error'] = True
        else:     
            context['error'] = False
            request.session['id_token_generator'] = id
            context['link'] = link
        return render(request, 'dtcapp/index.html',context)


class Home(AuthView):
    template_name = "dtcapp/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # -- FOLLOWS --
        follows =  self.request.user.Follows.annotate(
            activated=F('following__activated'),
            following_id=F('following')
        )
        context['follows'] = follows

        # -- TOP --
        txt_top = self.kwargs.get('top', None)
        if txt_top is None:
            txt_top='24H'
        context['top'] = txt_top

        # -- CLIPS --
        top = TwitchTop.string_to_top(txt_top)

        follow_ids = list(follows.filter(activated=True).values_list('id_streamer',flat=True))
        
        twitchClip = TwitchClip(follow_ids)

        clips = twitchClip.get_clips_from_all_followed(twitchTop=top)
        list_clip_urls = []

        '''
        for clip_data in clips.values(): #by streamer
            for clip in clip_data['data']: #by clip
                list_clip_urls.append(f"{clip['embed_url']}&parent=localhost&parent=127.0.0.1")
                print(clip['embed_url'])
        '''

        list_clip_urls.append("https://clips.twitch.tv/embed?clip=FamousKitschyElephantRickroll-jzd7ZqFBGOX8n6Mh&parent=localhost&parent=127.0.0.1")
        list_clip_urls.append("https://clips.twitch.tv/embed?clip=ExpensiveDelightfulScorpionStrawBeary-6r9WE45noXxZKwt3&parent=localhost&parent=127.0.0.1")
        context['clips'] = list_clip_urls

        return context

class FollowingSwitch(AuthView):

    def post(self, request):
        following_id = request.POST['following_id']
        print(f"following_id:{following_id}")
        if following_id is not None:
            following = Following.objects.get(pk=following_id)
            if following is not None:
                following.activated = not following.activated
                following.save()
                #TODO: with message success ?
                return redirect('home')
            else:
                pass #TODO: redirect with error message !!!
        else:
            pass #TODO: redirect with error message !!!



class Profile(AuthView):
    template_name = "dtcapp/profile.html"


class Subscriptions(AuthView):
    template_name = "dtcapp/subcriptions.html"


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

            log_into(self.request, user)

            return super(UserCreateView, self).form_valid(form)
        else:
            messages.error(self.request,'ID Twitch has been changed.')
            return redirect('user-create')
        

def signup(request):

    # Cannot signup if already authenticated
    if request.user.is_authenticated:
        return redirect('home')

    twitch_user = TwitchUser(id_generator=request.session['id_token_generator'])

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

    if request.method == 'POST':

        user = authenticate(
            username=request.POST['username'], password=request.POST['password'])

        if user is not None:
            log_into(request, user)
            return redirect('home')
        else:
            return redirect('login')

    elif request.method == 'GET':

        # Cannot access the login page if authenticated already
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'dtcapp/login.html')


def logout(request):

    if request.user.is_authenticated:
        logout_of(request)

    return redirect('index')


class TwitchTest(AuthView):
    template_name = "dtcapp/test-twitch.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        '''
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
        '''
        return context
