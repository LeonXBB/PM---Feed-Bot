from decouple import config

from ...bin.utils import Utils
from ..Screen import Screen


class NewEventMenuNonReady(Screen):

    def get_keyboards(self, data=None, via=None):
        
        edit_home_team_name = {"text": self.strings[1][0], "data": "0_0"}
        edit_away_team_name = {"text": self.strings[1][1], "data": "0_1"}
        edit_match_date = {"text": self.strings[1][2], "data": "1_0"}
        edit_match_time = {"text": self.strings[1][3], "data": "1_1"}
        edit_competition_name = {"text": self.strings[1][4], "data": "2_0"}
        edit_rules_set = {"text": self.strings[1][5], "data": "3_0"}
        clear = {"text": self.strings[1][6], "data": "4_0"}
        go_back = {"text": self.strings[1][7], "data": "4_1"}
        cancel = {"text": self.strings[1][8], "data": "5_0"} # if you're having problems with this, that's because there is no string for this button in your db.

        layout = [(edit_home_team_name, edit_away_team_name), (edit_match_date, edit_match_time), (edit_competition_name, edit_rules_set), (clear, go_back, cancel)]
        
        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "21", "NewEventMenuNonReady", bot_strings)

    def button_0(self, params, user_id): # team name
        
        if params[0] == "0":
            return Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "show_screen_to", "params": ["22", [], ]} #TODO move static formatters into screen class?
            )[0]
        elif params[0] == "1":
            return Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "show_screen_to", "params": ["23", [], ]} #TODO move static formatters into screen class?
            )[0]

    def button_1(self, params, user_id): # match date\time
        
        if params[0] == "0":
            return Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "show_screen_to", "params": ["24", [], ]} #TODO move static formatters into screen class?
            )[0]
        elif params[0] == "1":
            return Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "show_screen_to", "params": ["25", [], ]} #TODO move static formatters into screen class?
            )[0]

    def button_2(self, params, user_id): # competition name
        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["27", [], ]} #TODO move static formatters into screen class?
        )[0]

    def button_3(self, params, user_id): # rules set
        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["26", [], ]} #TODO move static formatters into screen class?
        )[0]

    def button_4(self, params, user_id): # clear / to the menu
        
        code = params[0]

        if code == "0": # clear
            
            event_id = Utils.api("get", 
            model="Event",
            params={"admin_id": user_id, "status": 0},
            fields=["id"], 
            )[0][0]
        

            Utils.api("update", 
            model="Event", 
            filter_params={"id": event_id}, 
            update_params={"status": 5}
            )

        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["10", [[config("telebot_version")], ], ]} #TODO move static formatters into screen class?
        )[0]

    def button_5(self, params, user_id): # cancel edit

        from ...models import Event, EventTemplateEdit

        event = Event._get_({"admin_id": user_id, "status": 0})[0]
        template_edit = EventTemplateEdit._get_({"event_id": event.id})[-1]
        template_edit.undo()

        return event.show_template()
