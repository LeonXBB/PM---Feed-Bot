from ..Screen import Screen


class MainMenu(Screen):

    def __init__(self) -> None:
        super().__init__("10", "MainMenu")
    
    def text(self, text, user):
        print('main menu')