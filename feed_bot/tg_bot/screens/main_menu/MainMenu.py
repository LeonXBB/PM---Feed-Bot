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

        layout = [(new_event,), (event_list,), (rules_set,), (language_edit,), (exit,)]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "10", "MainMenu")
           
    def button_0(self, params, user_id): # new event
        
        # get or make template
        # check check its preparedness
        # send json to site
        # return correct screen

        event_id, home_team_id, away_team_id, event_competition_id, rules_set_id, epoch_scheduled = Utils.api("get_or_make",
        model="Event",
        params={"admin_id": user_id, "status": 0, "created": f"{int(time.time())};{user_id}"},
        fields=["id", "home_team_id", "away_team_id", "event_competiton_id", "rules_set_id, epoch_scheduled"], 
        )[0]

        home_team_name = Utils.api("get",
        model="Team",
        params={"id": home_team_id},
        fields=["name"]
        ) 
        away_team_name = Utils.api("get",
        model="Team",
        params={"id": away_team_name},
        fields=["name"]
        )
        for team_name in [home_team_name, away_team_name]:
            if len(team_name) == 0:
                team_name = ""

        event_competition_name = 0
        
        rules_set_name = 0

        match_date = 0
        match_time = 0

        ready = False

        if ready: 
            return Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "show_screen_to", "params": ["20", [[event_id, home_team_name, away_team_name, event_competition_name, rules_set_name, match_date, match_time], []]]}
            )[0] # TODO formatters static (again), made into a function to avoid redundancy

        else:
            return Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "show_screen_to", "params": ["21", []]}
            )[0]

    def button_1(self, params, user_id): # event list
        print("event_list")

    def button_2(self, params, user_id): # set rules editor
        print("set rules editor")

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