from ....bin.utils import Utils
from ..Remainder import Remainder


class PeriodEnd(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        end = {"text": self.strings[1][0], "data": "r_0_11_{}"}

        layout = [(end,),]

        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "111", "PeriodEnd", bot_strings)

    def button_0(self, params, user_id, scheduled_message_id):
        
        return Utils.api("execute_method",
        model="Period",
        params={"id": int(params[0])},
        method={"name": "end", "params": []}
        )[0]