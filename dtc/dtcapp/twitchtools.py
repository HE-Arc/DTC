from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope

from django.conf import settings

class TwitchUser:
    TARGET_SCORE = [AuthScope.USER_READ_EMAIL]
    MAX_FOLLOWS = 100
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
            print(self.user)
            return self.user['id']
    
    def get_user_following(self):
        if self.user is not None:
            return self.twitch.get_users_follows(from_id=self.get_user_id(), first=TwitchUser.MAX_FOLLOWS)