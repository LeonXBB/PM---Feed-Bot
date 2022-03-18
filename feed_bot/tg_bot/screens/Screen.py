from ..models import String


class Screen(): #TODO change into django model?
    
    screens = []

    @classmethod
    def _get_(cls, name=None, id=None):
        
        for screen in cls.screens:
            if ((screen.screen_id == id or id is None) and (screen.screen_name == name or name is None)): 
                return screen

    def get_texts(self):
        
        rv = [[],]

        for string in String.objects.all():
            if string.screen_id == self.screen_id:
                while string.position_index > len(rv):
                    rv.append(list())
                rv[string.position_index].append(string)

        return rv

    def get_keyboards(self):
        return None

    def _get_button_count_(self):
        
        rv = 0

        if self.keyboard is not None:
            for row in self.keyboard:
              rv += len(row)

        return rv

    def __init__(self, screen_id=-1, screen_name="") -> None:

        self.screen_id = screen_id
        self.screen_name = screen_name
    
        self.strings = self.s()
        self.keyboards = self.get_keyboards()

        self.screens.append(self)
        
        for i in range(self._get_button_count_()):
            if not hasattr(self, f"button_{i}"): setattr(self, f"button_{i}", lambda self, params, user: None)

    def text(self, text, user):
        pass

    def show(self):
        return self.strings, self.keyboards 