from ..Remainder import Remainder


class TimeOutEnd(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_21_{}"}
        
        layout = [(ok,),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "121", "TimeOutStart")

    def button_0(self, params, user_id, scheduled_message_id):
        return None #TODO restore active screen