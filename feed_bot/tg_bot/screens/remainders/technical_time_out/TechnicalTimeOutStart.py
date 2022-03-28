from ....bin.utils import Utils
from ..Remainder import Remainder


class TechnicalTimeOutStart(Remainder):

    def get_keyboards(self):
        
        start = {"text": self.strings[1][0], "data": "r_0_30_{}"}
        skip = {"text": self.strings[1][1], "data": "r_1_30_{}"}
        
        layout = [(start, skip),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "130", "TechnicalTimeOutStart")

    def button_1(self, params, user_id, scheduled_message_id): # skip  
        
        pass #TODO write