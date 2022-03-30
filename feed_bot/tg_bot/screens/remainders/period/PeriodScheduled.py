from ....bin.utils import Utils
from ..Remainder import Remainder

class PeriodScheduled(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_14_{}"}
        start = {"text": self.strings[1][1], "data": "r_1_14_{}"}

        layout = [(ok, start),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "114", "PeriodScheduled")

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