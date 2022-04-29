from decouple import config

from ..Screen import Screen
from ...bin.utils import Utils


class EventList(Screen):

    def get_keyboards(self, data=None, via=None):
        
        go_back = {"text": self.strings[1][0], "data": "0_0"}

        layout = [(go_back,), ]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "40", "EventList")

    def button_0(self, params, user_id):
        
        return Utils.api("execute_method",
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["10", [[config("telebot_version")]]]} #TODO static formatters into separate file
        )[0]