from django.shortcuts import render, redirect
from django.views import generic, View
from django.urls import reverse_lazy

from .models import User, Following, LikedClip

from .twitchtools import TwitchUser, TwitchClip, TwitchTop, TwitchToken

from django.contrib import messages
from django.conf import settings

from .forms import SignUpForm

from django.contrib.auth import login as log_into
from django.contrib.auth import logout as logout_of
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_protect

from django.db import IntegrityError
from django.db.models import F
from django.http import JsonResponse

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
    return TwitchToken.redirect_with_link(request,'dtcapp/index.html')


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

        value_likes = 'LIKES'

        list_tops = ['24H','7D','ALL']
        list_tops.append(value_likes)
        # -- TOP --
        txt_top = self.kwargs.get('top', None)
        if txt_top is None or txt_top not in list_tops:
            txt_top='24H'

        context['top'] = txt_top

        # -- CLIPS --
        if txt_top != value_likes:
            top = TwitchTop.string_to_top(txt_top)

            follow_ids = list(follows.filter(activated=True).values_list('id_streamer', flat=True))
            
            twitchClip = TwitchClip(follow_ids)

            clips = twitchClip.get_clips_from_all_followed(twitchTop=top)
            list_clips = []

            for clip_data in clips.values(): #by streamer
                for clip in clip_data['data']: #by clip
                    list_clips.append({
                        'id' : clip['id'],
                        'title' : f"{clip['title']}" if len(clip['title']) < 35 else f"{clip['title'][:30]} ...",
                        'embed_url' : f"{clip['embed_url']}&parent={settings.CLIP_PARENT}",
                        'thumbnail_url' : f"{clip['thumbnail_url']}"
                        })

            context['clips'] = list_clips
            context['is_likes'] = False
        else:
            subscriptions = self.request.user.Subscriptions.all()
            list_clips = []
            for subscription in subscriptions:
                clips = subscription.Likes.all()
                for clip in clips:
                    list_clips.append({
                        'id':clip.id_clip,
                        'title': f"{clip.title_clip}" if len(clip.title_clip) < 35 else f"{clip.title_clip[:30]} ...",
                        'embed_url' : f"{clip.clipURL}&parent={settings.CLIP_PARENT}",
                        'thumbnail_url' : clip.thumbnailURL_clip,
                        'liked_by' : subscription.username
                    })

            context['clips'] = list_clips
            context['is_likes'] = True

        # -- LIKED CLIPS OF THE USER --

        likedclip_id_clips = self.request.user.Likes.all().values_list('id_clip', flat=True)

        context['likedclips'] = likedclip_id_clips

        # -- SAY IT IS A 'HOME' PAGE --

        context['is_home'] = True

        return context

class FollowingSwitch(AuthView):

    def post(self, request):
        following_id = request.POST['following_id']
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


# User.objects.get(username=the_username).pk

class Like(AuthView):

    def get(self, request):

        return redirect('home')

    def post(self, request):

        id_clip = request.POST['id_clip']
        clipURL = request.POST['clipURL']
        title_clip = request.POST['title_clip']
        thumbnailURL_clip = request.POST['thumbnailURL_clip']

        try : # Tries to save a new liked clip in the database

            likedclip = LikedClip(clipURL = clipURL, id_clip = id_clip, title_clip = title_clip, thumbnailURL_clip = thumbnailURL_clip)
            likedclip.save()
            
        except IntegrityError : # Chose to ignore the IntegrityError (if clip already exists in the LikedClip table)

            pass # This Exception is thrown when already exists in table, we DON'T want this error to stop everything

        except : # If it is another Exception than IntegrityError, we WANT this error to be caught and dealt with later
            
            return # Because it doesn't return anything, it allows the error to be detected later in the javascript

        request.user.Likes.add(LikedClip.objects.get(id_clip = id_clip))
        
        data = {'action': 'like' }
        return JsonResponse(data, safe=False)

class Dislike(AuthView):

    def get(self, request):

        return redirect('home')

    def post(self, request):

        id_clip = request.POST['id_clip']
        disliked_clip = LikedClip.objects.get(id_clip = id_clip)

        #TODO:Maybe do the all() after the filter ? (sinon on prend tous les objets depuis la DB et après on les filtre côté python)
        nb_users = len(User.Likes.through.objects.all().filter(likedclip = disliked_clip)) # nb of users who liked this clip also

        request.user.Likes.remove(LikedClip.objects.get(id_clip = id_clip))

        if nb_users < 2 :
            disliked_clip.delete()       

        data = {'action': 'dislike' }
        return JsonResponse(data, safe=False)

class Profile(AuthView):
    template_name = "dtcapp/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        list_likedclips = self.request.user.Likes.all()

        context['likedclips'] = list_likedclips

        context['is_profile'] = True

        return context

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
            return TwitchToken.redirect_with_link(request,'dtcapp/login.html')

    elif request.method == 'GET':
        return TwitchToken.redirect_with_link(request,'dtcapp/login.html')


class SyncFollows(AuthView):
    def get(self, request):
        user = request.user
        twitch_user = TwitchUser(id_user=user.id_twitch)
        followers = twitch_user.get_user_following()
        followers_ids = [follower['to_id'] for follower in followers['data']]
        user.update_follows(followers_ids)
        return redirect('home')

def logout(request):

    if request.user.is_authenticated:
        logout_of(request)

    return redirect('index')

class Follow(AuthView):

    def get(self, request):

        return redirect('subscriptions')

    def post(self, request):

        user_id = request.POST['user_id']
        user_subscribed = None
        try : # Tries to save a new liked clip in the database
            user_subscribed = User.objects.get(id=user_id)
            request.user.Subscriptions.add(user_subscribed)
            
        except IntegrityError : # Chose to ignore the IntegrityError (if clip already exists in the LikedClip table)

            pass # This Exception is thrown when already exists in table, we DON'T want this error to stop everything

        except : # If it is another Exception than IntegrityError, we WANT this error to be caught and dealt with later
            
            return # Because it doesn't return anything, it allows the error to be detected later in the javascript
        subscriptions = request.user.Subscriptions.all()
        
        data = {'action': 'follow', 'user_id' : user_id , 'user_name':user_subscribed.username,'user_picture':user_subscribed.pictureURL}
        return JsonResponse(data, safe=False)

class Unfollow(AuthView):

    def get(self, request):

        return redirect('subscriptions')

    def post(self, request):

        user_id = request.POST['user_id']
        
        request.user.Subscriptions.remove(User.objects.get(id=user_id))
        #subscription_deleted = 

        data = {'action': 'unfollow','user_id' : user_id}
        return JsonResponse(data, safe=False)

class Subscriptions(AuthView):
    template_name = "dtcapp/subscriptions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Search username

        username = self.request.GET.get('username',None)
        if username is not None and username is not '':
            users = User.objects.filter(username__contains=username).all()
            context['searched'] = True
            context['users'] = users
        else:
            context['searched'] = False

        #Get subscriptions

        subscriptions = self.request.user.Subscriptions.all()

        context['subscriptions_id'] = subscriptions.values_list('id', flat=True)

        context['subscriptions'] = subscriptions

        context['is_subscriptions'] = True

        return context