from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope

from django.conf import settings

class TwitchUser:
    TWITCH=Twitch(settings.TWITCH_PUBLIC_KEY,settings.TWITCH_PRIVATE_KEY)

    def __init__(self,token=None, refresh_token=None, user=None):
        if token is not None and refresh_token is not None:
            self.token = token
            self.refresh_token = refresh_token
        else:
            self.token,self.refresh_token = self._twitch_auth()

        if self.token is not None and self.refresh_token is not None:
            if user is not None:
                self.user = user
            else:
                self.user = self._get_user_info()
        else:
            self.user = None

    def _twitch_auth(self):
        target_scope = [AuthScope.USER_READ_EMAIL]
        auth = UserAuthenticator(TwitchUser.TWITCH, target_scope, force_verify=False)
        # this will open your default browser and prompt you with the twitch verification website
        token, refresh_token = auth.authenticate()
        print(f'TOKEN : {token}')
        # add User authentication
        TwitchUser.TWITCH.set_user_authentication(token, target_scope, refresh_token)

        return token, refresh_token

    def _get_user_info(self):
        """Get user info if user is authentificated.

        Returns:
            dict: User info None if not authentificated.
        """
        return TwitchUser.TWITCH.get_users()

    def get_user_id(self):
        if self.user is not None:
            return self.user['data']['id']
    
    def get_user_following(self):
        if self.user is not None:
            return TWITCH.get_users_follows(to_id=self.get_user_id())