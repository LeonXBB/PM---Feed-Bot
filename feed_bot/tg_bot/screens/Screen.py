from decouple import config

import requests

from ..bin.utils import Utils

class Screen(): #TODO change into django model?
    
    screens = []

    @classmethod
    def _get_(cls, name=None, id=None):
        
        for screen in cls.screens:
            if ((screen.screen_id == id or id is None) and (screen.screen_name == name or name is None)): 
                return screen

    def get_strings(self, via):

        def via_server():
            
            from ..models import TextString

            strings = {}

            all_strings = TextString.objects.all()
            for string_ in all_strings:
                if string_.screen_id == self.screen_id:
                    if string_.position_index not in list(strings.keys()):
                        strings[string_.position_index] = list()
                    strings[string_.position_index].append([string_.language_1, string_.language_2, string_.language_3, string_.language_4, string_.language_5])

            return strings

        def via_bot(): # TODO rewrite as to make one big request instead of a lot of small ones
            strings = {}

            i = 0
            while True:
            
                res = Utils.api("get",
                model="TextString",
                fields=["language_1", "language_2", "language_3", "language_4", "language_5"],
                params={"screen_id": self.screen_id, "position_index": i}
                )
                
                if len(res) == 0:
                    break
                else:
                    strings[i] = [*res, ]
                    i += 1

            return strings

        if via == "server":
            return via_server()

        elif via == "bot":
            return via_bot()

    def get_keyboards(self):
        return []

    def __init__(self, via, screen_id="-1", screen_name="") -> None:

        self.screen_id = screen_id
        self.screen_name = screen_name
    
        self.strings = self.get_strings(via)
        self.keyboards = self.get_keyboards()

        self.screens.append(self)

    def show(self):
        return self.strings, self.keyboards 