from feed_bot.tg_bot.screens.Screen import Screen


class AuthorizationInvitation(Screen):

    def __init__(self) -> None:
        super().__init__("10", "AuthorizationInvitation")
    
    def text(self, text, user):
        print('main menu')