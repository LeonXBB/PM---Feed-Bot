from decouple import config
import requests


class Screen(): #TODO change into django model?
    
    screens = []

    @classmethod
    def _get_(cls, name=None, id=None):
        
        for screen in cls.screens:
            if ((screen.screen_id == id or id is None) and (screen.screen_name == name or name is None)): 
                return screen

    def get_texts(self):
    
        strings = requests.post(f"{config('server_address')}/api", json={"task": "get", "class": "TextString", "fields": ["language_1", "language_2", "language_3", "language_4", "language_5"], "params": {"screen_id": self.screen_id}})

        try:
            return strings.json()[0]
        except:
            return strings.json() #TODO hack for when we don't have string for all the screens. Remove in production

    def get_keyboards(self):
        return None

    def _get_button_count_(self):
        
        rv = 0

        if self.keyboards is not None:
            for keyboard in self.keyboards:
                for row in keyboard:
                    rv += len(row)

        return rv

    def __init__(self, screen_id=-1, screen_name="") -> None:

        self.screen_id = screen_id
        self.screen_name = screen_name
    
        self.strings = self.get_texts()
        self.keyboards = self.get_keyboards()

        self.screens.append(self)
        
        for i in range(self._get_button_count_()):
            if not hasattr(self, f"button_{i}"): setattr(self, f"button_{i}", lambda self, params, user: None)

    def text(self, text, user):
        pass

    def show(self):
        return self.strings, self.keyboards 