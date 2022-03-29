from ..Remainder import Remainder


class EventEnded(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_05_{}"}

        layout = [(ok,),]

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "105", "EventEnded")
