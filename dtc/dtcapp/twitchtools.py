from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope

from django.conf import settings

#For TwichClips
from enum import Enum, auto
from datetime import datetime, timedelta

class TwitchUser:
    TARGET_SCORE = [AuthScope.USER_READ_EMAIL]
    MAX_FOLLOWS = 3
    def __init__(self,token=None, refresh_token=None, user=None):
        self.twitch = Twitch(settings.TWITCH_PUBLIC_KEY,settings.TWITCH_PRIVATE_KEY)
        if token is not None and refresh_token is not None:
            self.token = token
            self.refresh_token = refresh_token
            self.twitch.set_user_authentication(self.token, TwitchUser.TARGET_SCORE, self.refresh_token)
        else:
            self.token,self.refresh_token = self._twitch_auth()

        if self.token is not None and self.refresh_token is not None:
            if user is not None:
                self.user = user
            else:
                self.user = self._get_user_info()
        else:
            self.user = None

        #App authentification
        self.twitch.authenticate_app([])

    def _twitch_auth(self):
        auth = UserAuthenticator(self.twitch, TwitchUser.TARGET_SCORE, force_verify=False)
        # this will open your default browser and prompt you with the twitch verification website
        token, refresh_token = auth.authenticate()
        print(f'TOKEN : {token}')
        # add User authentication
        self.twitch.set_user_authentication(token, TwitchUser.TARGET_SCORE, refresh_token)

        return token, refresh_token

    def _get_user_info(self):
        """Get user info if user is authentificated.

        Returns:
            dict: User info None if not authentificated.
        """
        return self.twitch.get_users()['data'][0]

    def get_user_id(self):
        if self.user is not None:
            #print(self.user)
            return self.user['id']
    
    def get_user_following(self):
        if self.user is not None:
            return self.twitch.get_users_follows(from_id=self.get_user_id(), first=TwitchUser.MAX_FOLLOWS)


class TwitchTop(Enum):
    LAST_24H=auto()
    LAST_7D=auto()
    ALL_TIME=auto()

class TwitchClip:
    MAX_CLIPS=2
    def __init__(self, followed_ids):
        self.twitch = Twitch(settings.TWITCH_PUBLIC_KEY,settings.TWITCH_PRIVATE_KEY)
        self.followed_ids = followed_ids
        #App authentification
        self.twitch.authenticate_app([])

    def get_infos_followed(self):
        users_followed = self.twitch.get_users(user_ids =self.followed_ids)
        names_followed =[user['display_name'] for user in users_followed['data']]
        pictures_followed = [user['profile_image_url'] for user in users_followed['data']]
        return names_followed, pictures_followed

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