from ....bin.utils import Utils
from ..Remainder import Remainder


class EventStart(Remainder):

    def get_keyboards(self):
        
        start = {"text": self.strings[1][0], "data": "r_0_00_{}"}

        layout = [(start,),]

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "100", "EventStart")

    def button_0(self, params, user_id, scheduled_message_id):

        period_id = Utils.api("get",
        model="Period",
        params={"event_id": int(params[0]), "status": 0},
        fields=["id"],)[0][0]

        return Utils.api("execute_method",
        model="Period",
        params={"id": period_id},
        method={"name": "run", "params": []}
        )[0]