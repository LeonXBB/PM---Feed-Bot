from ....bin.utils import Utils
from ..Remainder import Remainder

class EventScheduled(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_04_{}"}
        start = {"text": self.strings[1][1], "data": "r_1_04_{}"}

        layout = [(ok, start),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "104", "EventScheduled")

    def button_1(self, params, user_id, scheduled_message_id):      
        
        return Utils.api("execute_method",
        model="Event",
        params={"id": int(params[0])},
        method={"name": "run", "params": []}
        )[0]