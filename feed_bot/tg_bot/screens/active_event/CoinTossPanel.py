from decouple import config

from ...bin.utils import Utils
from ..Screen import Screen


class CoinTossPanel(Screen):

    def get_keyboards(self):
        
        left_team = {"text": self.strings[1][0], "data": "0_{}"}
        ball_control = {"text": self.strings[1][1], "data": "1_{}"}

        main_menu = {"text": self.strings[1][2], "data": "2_{}"}
        save = {"text": self.strings[1][3], "data": "3_{}"}

        layout = ((left_team,), (ball_control, ), (main_menu, save))
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "32", "CoinTossPanel")

    def button_0(self, params, user_id): # left team
        
        return Utils.api("execute_method",
        model="CoinToss",
        params={"id": int(params[0])},
        method={"name": "swipe", "params": ["left_team_id",]},
        )[0]

    def button_1(self, params, user_id): # ball control
        
        return Utils.api("execute_method",
        model="CoinToss",
        params={"id": int(params[0])},
        method={"name": "swipe", "params": ["ball_possesion_team_id",]},
        )[0]

    def button_2(self, params, user_id): # main menu
        
        return Utils.api("execute_method",
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["10", [[config("telebot_version")], ]]}
        )[0]

    def button_3(self, params, user_id): # save

        return Utils.api("execute_method",
        model="CoinToss",
        params={"id": int(params[0])},
        method={"name": "save_results", "params": []}
        )[0]