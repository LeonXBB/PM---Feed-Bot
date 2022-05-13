from decouple import config

from ..bin.utils import Utils

class Screen():
        
    screens = []

    @classmethod
    def _get_(cls, name=None, id=None):
        
        for screen in cls.screens:
            if ((screen.screen_id == id or id is None) and (screen.screen_name == name or name is None)): 
                return screen

    def get_strings(self, via, bot_strings=None):

        def via_server():
            
            from ..models import TextString

            strings = {}

            all_strings = TextString.objects.all().order_by("id")
            for string_ in all_strings:
                if string_.screen_id == self.screen_id or (string_.screen_id == self.screen_id[1:] and self.screen_id[0] == "0"):
                    if string_.position_index not in list(strings.keys()):
                        strings[string_.position_index] = list()
                    strings[string_.position_index].append([string_.language_1, string_.language_2, string_.language_3, string_.language_4, string_.language_5])

            return strings

        def via_bot(bot_strings):
            return bot_strings if bot_strings is not None else {}
            #strings = {}

            '''i = 0
            while True:
            
                res = Utils.api("get",
                model="TextString",
                fields=["language_1", "language_2", "language_3", "language_4", "language_5"],
                params={"screen_id": self.screen_id, "position_index": i},
                order_by=["id",]
                )
                
                if len(res) == 0:
                    break
                else:
                    strings[i] = [*res, ]
                    i += 1'''
            
            #request_results = Utils.api("get",
            #model="TextString",
            #fields=["position_index", "language_1", "language_2", "language_3", "language_4", "language_5"],
            #params={"screen_id": self.screen_id},)

            #for request_result in request_results:
            #    if request_result[0] not in list(strings.keys()):
            #        strings[request_result[0]] = list()
            #    strings[request_result[0]].append([request_result[1], request_result[2], request_result[3], request_result[4], #request_result[5]])
            

            #return strings

        if via == "server":
            return via_server()

        elif via == "bot":
            return via_bot(bot_strings)

    def get_keyboards(self, data=None, via=None):
        return []

    def __init__(self, via, screen_id="-1", screen_name="", bot_strings=None) -> None:

        self.screen_id = screen_id
        self.screen_name = screen_name
    
        self.strings = self.get_strings(via, bot_strings)
        self.keyboards = self.get_keyboards(None, via)

        self.screens.append(self)

        if via == "server":
            with open("screen_strings.txt", "a", encoding="utf-8") as file:
                file.write(f"'{screen_name}': {self.strings},\n")

    def show(self):
        return self.strings, self.keyboards 