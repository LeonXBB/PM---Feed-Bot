from ....bin.utils import Utils
from ..Remainder import Remainder


class EventAboutToStart(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_02_{}"}
        start_now = {"text": self.strings[1][1], "data": "r_1_02_{}"}

        layout = [(ok, start_now),]

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "102", "EventAboutToStart")

    def button_1(self, params, user_id, scheduled_message_id):
        
        return Utils.api("execute_method", # TODO figure out
        model="Event",
        params={"id": int(params[0])},
        method={"name": "run", "params": ["init",]}
        )[0]