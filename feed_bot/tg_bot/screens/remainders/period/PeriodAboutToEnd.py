from ....bin.utils import Utils
from ..Remainder import Remainder


class PeriodAboutToEnd(Remainder):
    
    def get_keyboards(self, data=None, via=None):
        
        ok = {"text": self.strings[1][0], "data": "r_0_13_{}"}
        end_now = {"text": self.strings[1][1], "data": "r_1_13_{}"}

        layout = [(ok, end_now),]

        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "113", "PeriodAboutToEnd", bot_strings)

    def button_1(self, params, user_id, scheduled_message_id):
        
        return Utils.api("execute_method",
        model="Period",
        params={"id": int(params[0])},
        method={"name": "end", "params": []}
        )[0]