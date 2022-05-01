from ....bin.utils import Utils
from ..Remainder import Remainder


class PeriodAboutToStart(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        ok = {"text": self.strings[1][0], "data": "r_0_12_{}"}
        start_now = {"text": self.strings[1][1], "data": "r_1_12_{}"}

        layout = [(ok, start_now),]

        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "112", "PeriodAboutToStart", bot_strings)

    def button_1(self, params, user_id, scheduled_message_id):
        
        Utils.api("execute_method",
        model="Period",
        params={"id": int(params[0])},
        method={"name": "launch", "params": []}
        )

        return Utils.api("execute_method",
        model="Period",
        params={"id": int(params[0])},
        method={"name": "run", "params": ["show_"]}
        )[0]