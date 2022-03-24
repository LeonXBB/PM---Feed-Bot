from ..Remainder import Remainder


class EventScheduled(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_04_test"}
        start = {"text": self.strings[1][1], "data": "r_1_04_test"}

        layout = [(ok, start),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "104", "EventScheduled")

    def button_1(self, params, user_id):
        pass