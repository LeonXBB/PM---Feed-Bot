from ...bin.utils import Utils
from ..Screen import Screen


class CoinTossPanel(Screen):

    def get_keyboards(self):
        
        left_team = {"text": self.strings[1][0], "data": "0_0_{}"}
        ball_control = {"text": self.strings[1][1], "data": "1_0_{}"}

        main_menu = {"text": self.strings[1][2], "data": "2_0_{}"}
        save = {"text": self.strings[1][3], "data": "3_0_{}"}

        layout = ((left_team,), (ball_control, ), (main_menu, save))
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "32", "CoinTossPanel")

    def button_0(self, params, user_id):
        pass

    def button_1(self, params_user_id):
        pass

    def button_2(self, params, user_id):
        pass

    def button_3(self, params, user_id):
        pass