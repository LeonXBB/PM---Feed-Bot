from decouple import config

from ..Screen import Screen
from ...bin.utils import Utils

class ExitConfirmation(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "12", "ExitConfirmation")

    def get_keyboards(self, data=None, via=None):
        
        yes = {"text": self.strings[1][0], "data": "0_0"}
        no = {"text": self.strings[1][1], "data": "1_0"}
        
        layout = [(yes, no),]
        
        return [layout,]

    def button_0(self, params, user_id):
        Utils.api("update",
        model="BotUser",
        filter_params={"id": user_id},
        update_params={"is_logged_in": 0}
        )
        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["00", ]}
        )[0]

    def button_1(self, params, user_id):
        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["10", [[config("telebot_version")], ]]} #TODO move static formatters into screen class?
        )[0]
