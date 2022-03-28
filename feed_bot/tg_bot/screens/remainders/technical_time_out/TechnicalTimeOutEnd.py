from ..Remainder import Remainder


class TechnicalTimeOutEnd(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_31_{}"}
        
        layout = [(ok,),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "131", "TechnicalTimeOutEnd")

    def button_0(self, params, user_id, scheduled_message_id):
        return None #TODO restore active screen