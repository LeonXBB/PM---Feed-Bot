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
        
        return Utils.api("execute_method", # TODO figure out
        model="Event",
        params={"id": int(params[0])},
        method={"name": "run", "params": ["init"]}
        )[0]