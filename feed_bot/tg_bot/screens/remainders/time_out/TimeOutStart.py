from ..Remainder import Remainder


class TimeOutStart(Remainder):

    def get_keyboards(self):
        
        start = {"text": self.strings[1][0], "data": "r_0_20_0"}
        skip = {"text": self.strings[1][1], "data": "r_1_20_0"}
        
        layout = [(start, skip),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "120", "TimeOutStart")

    def button_1(self, params, user_id, scheduled_message_id): # skip  
        
        pass #TODO write