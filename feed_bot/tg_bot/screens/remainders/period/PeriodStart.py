from ....bin.utils import Utils
from ..Remainder import Remainder


class PeriodStart(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        start = {"text": self.strings[1][0], "data": "r_0_10_{}"}

        layout = [(start,),]

        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "110", "PeriodStart", bot_strings)

    def button_0(self, params, user_id, scheduled_message_id):
        
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