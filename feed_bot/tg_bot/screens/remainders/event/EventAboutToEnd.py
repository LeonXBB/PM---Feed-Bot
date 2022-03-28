from ....bin.utils import Utils
from ..Remainder import Remainder


class EventAboutToEnd(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_03_{}"}
        end_now = {"text": self.strings[1][1], "data": "r_1_03_{}"}

        layout = [(ok, end_now),]

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "103", "EventAboutToEnd")

    def button_1(self, params, user_id, scheduled_message_id):
        
        return Utils.api("execute_method",
        model="Event",
        params={"id": int(params[0])},
        method={"name": "end", "params": []}
        )[0]