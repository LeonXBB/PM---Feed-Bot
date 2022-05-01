from decouple import config

from ...bin.utils import Utils
from ..Screen import Screen


class ControlPanelPaused(Screen):

    def get_keyboards(self, data=None, via=None):
        
        resume = {"text": self.strings[1][0], "data": "0_{}"}
     
        cancel = {"text": self.strings[1][1], "data": "1_{}"}
        main_menu = {"text": self.strings[1][2], "data": "2_{}"}
        
        layout = [(resume, ), (cancel, main_menu)]

        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:

        super().__init__(via, "31", "ControlPanelPaused", bot_strings)
            
    def button_0(self, params, user_id): # resume
        
        event_id = int(params[0])

        return Utils.api("execute_method",
        model="Period",
        params={"id": event_id},
        method={"name": "run", "params": ["pauseResume_"]}
        )[0]

    def button_1(self, params, user_id): # cancel
        pass

    def button_2(self, params, user_id): # main_menu
        
        return Utils.api("execute_method",
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["10", [[config("telebot_version")]]]} #TODO static formatters into separate file
        )[0]
