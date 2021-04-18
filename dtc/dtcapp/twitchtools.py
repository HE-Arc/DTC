from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope

from django.conf import settings
from django.shortcuts import render, redirect

#For TwichClips
from enum import Enum, auto
from datetime import datetime, timedelta

import base64
import urllib.request, json
import time

class TwitchToken:
    APPLICATION_NAME='DailyTWClip'
    TWITCH_GENERATOR='https://twitchtokengenerator.com/api/create/'
    TWITCH_STATUS='https://twitchtokengenerator.com/api/status/'
    SCOPES='user:read:email'
    

    #PING REQUEST
    TIMES=180
    WAITING_SECONDS=1

    @staticmethod
    def _get_name_base64():
        message = TwitchToken.APPLICATION_NAME
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message
        
    @staticmethod
    def get_link():
        link_generator = TwitchToken.TWITCH_GENERATOR+TwitchToken._get_name_base64()+'/'+TwitchToken.SCOPES
        print(link_generator)
        with urllib.request.urlopen(link_generator) as url:
            data = json.loads(url.read().decode())

            if data['success']:
                id = data['id']
                link = data['message']
                return id, link
            else:
                return None, None

    @staticmethod
    def get_token(id):
        link_generator = TwitchToken.TWITCH_STATUS+id
        times = TwitchToken.TIMES 
        while times > 0:
            print(f'BEFORE REQUEST {times}')
            url = urllib.request.urlopen(link_generator)
            print(f'BEFORE READING {times}')
            data = json.loads(url.read().decode())
            print(f'BEFORE CLOSING {times}')
            url.close()
            if data['success'] is False:
                times = times - 1
                time.sleep(TwitchToken.WAITING_SECONDS)
            else:
                token = data['token']
                refresh_token = data['refresh']
                client_id = data['client_id']
                return token, refresh_token, client_id

        return None, None, None

    @staticmethod
    def redirect_with_link(request,link_redirect):
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
            return render(request, link_redirect, context)


class TwitchUser:
    TARGET_SCOPE = [AuthScope.USER_READ_EMAIL]
    MAX_FOLLOWS = 10
    def __init__(self,id_generator=None, id_user=None):
        self.twitch = None
        self.id_generator = id_generator

        self.twitch = None
        self.twitch2 = Twitch(settings.TWITCH_PUBLIC_KEY,settings.TWITCH_PRIVATE_KEY)
        self.twitch2.authenticate_app([])

        if id_user is None:
            self.token,self.refresh_token = self._twitch_auth()
            self.user = self._get_user_info()
        else:
            self.user = {}
            self.user['id'] = id_user
        #print(f'\n\n\nYOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO : {self.user}\n\n\n')

        

    def _twitch_auth(self):
        #auth = UserAuthenticator(self.twitch, TwitchUser.TARGET_SCOPE, force_verify=False)
        # this will open your default browser and prompt you with the twitch verification website
        #token, refresh_token = auth.authenticate()


        if self.id_generator is not None:
            token, refresh_token, client_id = TwitchToken.get_token(self.id_generator)
            print(f'TOKEN : {token} | REFRESH_TOKEN : {refresh_token}')
            if client_id is not None:
                self.twitch = Twitch(client_id,settings.TWITCH_PRIVATE_KEY)
                # add User authentication
                self.twitch.set_user_authentication(token, TwitchUser.TARGET_SCOPE, refresh_token)
                # add App authentification
                
            else:
                token = None
                refresh_token = None     
        else:
            token = None
            refresh_token = None

        return token, refresh_token

    def _get_user_info(self):
        """Get user info if user is authentificated.

        Returns:
            dict: User info None if not authentificated.
        """

        if self.twitch is not None:
            return self.twitch.get_users()['data'][0]
        else:
            return None

    def get_user_id(self):
        if self.user is not None:
            #print(self.user)
            return self.user['id']

    def get_user_following(self):
        if self.user is not None:
            return self.twitch2.get_users_follows(from_id=self.get_user_id(), first=TwitchUser.MAX_FOLLOWS)


class TwitchTop(Enum):
    LAST_24H=auto()
    LAST_7D=auto()
    ALL_TIME=auto()

    @staticmethod
    def string_to_top(text):
        if text=='24H':
            return TwitchTop.LAST_24H
        elif text=='7D':
            return TwitchTop.LAST_7D
        elif text=="ALL":
            return TwitchTop.ALL_TIME
        
        return TwitchTop.LAST_24H # default

class TwitchClip:
    MAX_CLIPS=4
    def __init__(self, followed_ids):
        self.twitch = Twitch(settings.TWITCH_PUBLIC_KEY,settings.TWITCH_PRIVATE_KEY)
        self.followed_ids = followed_ids
        #App authentification
        self.twitch.authenticate_app([])

    def get_infos_followed(self):
        users_followed = self.twitch.get_users(user_ids =self.followed_ids)

        followers = {}

        for user in users_followed['data']:
            user_id = user['id']
            user_name = user['display_name']
            user_picture = user['profile_image_url']
            followers[user_id] = {'name':user_name,'picture':user_picture}

        return followers

        #names_followed =[user['display_name'] for user in users_followed['data']]
        #pictures_followed = [user['profile_image_url'] for user in users_followed['data']]
        #return names_followed, pictures_followed

    def get_datetimes(self,twitchTop):
        end = datetime.today()
        start = None
        if twitchTop == TwitchTop.LAST_7D:
            date_diff = timedelta(days = 7)
            start = end - date_diff
        elif twitchTop == TwitchTop.ALL_TIME:
            end = None
        else:# DEFAULT top == TwitchTop.LAST_24H
            date_diff = timedelta(days = 1)
            start = end - date_diff

        return start,end
    
    def get_clips_from_channel(self,broadcaster_id,twitchTop=TwitchTop.LAST_24H,n_clips=MAX_CLIPS,ended_at=None):
        start, end = self.get_datetimes(twitchTop)
        if ended_at is not None:
            end = ended_at

        clips = self.twitch.get_clips(broadcaster_id=broadcaster_id,first=n_clips,started_at=start,ended_at=end)
        return clips

    def get_clips_from_all_followed(self,twitchTop=TwitchTop.LAST_24H,n_clips=MAX_CLIPS,ended_at=None):
        clips = {}
        for flw_id in self.followed_ids:
            clips[flw_id] = self.get_clips_from_channel(flw_id,twitchTop=twitchTop,n_clips=n_clips,ended_at=ended_at)

        return clips