import hashlib

from ..Screen import Screen

class AuthorizationInvitation(Screen):

    def __init__(self) -> None:
        super().__init__("00", "AuthorizationInvitation")

    def text(self, text, user):

        from feed_bot.tg_bot.models import PasswordPair
               
        for password_pair in PasswordPair.objects.all():
            if password_pair.password_sha256 == hashlib.sha256(text).hexdigest():

                if password_pair.user_id == -1: password_pair.assign_to_user(user)

                return user.show_screen_to(self._get_(name="MainMenu"))

        return user.show_screen_to(self._get_(name="AuthorizationWrongPassword"))