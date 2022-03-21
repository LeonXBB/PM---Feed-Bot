from decouple import config

import time

from ...bin.utils import Utils
from ..Screen import Screen

class MainMenu(Screen):

    def get_keyboards(self):
        
        new_event = {"text": self.strings[1][0], "data": "0_0"}
        event_list = {"text": self.strings[1][1], "data": "1_0"}
        rules_set = {"text": self.strings[1][2], "data": "2_0"}
        language_edit = {"text": self.strings[1][3], "data": "3_0"}
        exit = {"text": self.strings[1][4], "data": "4_0"}

        #layout = [(new_event,), (event_list,), (rules_set,), (language_edit,), (exit,)] #TODO return it 
        
        layout = [(new_event,), (rules_set,), (language_edit,), (exit,)]
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "10", "MainMenu")
           
    def button_0(self, params, user_id): # new event
        
        # get or make template
        # send json to site
        # check its preparedness
        # return correct screen

        event_id = Utils.api("get_or_make",
        model="Event",
        params={"admin_id": user_id, "status": 0},
        fields=["id"], 
        )[0]

        if type(event_id) is list: event_id = event_id[0] #TODO fix

        Utils.api("test", "logic", desc="created new event template", arg1=event_id)

        rv = Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "show_template", "params": []}
        )[0]

        return rv

    def button_1(self, params, user_id): # event list
        
        events_ids = Utils.api("get",
        model="Event",
        params={"admin_id": user_id},
        fields=["id"])
        print(events_ids)
        
    def button_2(self, params, user_id): # set rules editor # TODO WRITE!
        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["10", [[config("telebot_version"),],]]}
        )[0]

    def button_3(self, params, user_id): # language_selection
        
        languages_names = []
        for language in Utils.api("get_all", model="TextLanguage"): languages_names.append(language[1])
            
        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["11", [["",], languages_names]]}
        )[0]

    def button_4(self, params, user_id): # exit
        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["12", []]}
        )[0]