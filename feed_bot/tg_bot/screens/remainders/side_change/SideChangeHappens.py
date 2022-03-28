from ..Remainder import Remainder


class SideChangeHappens(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_50_{}"}

        layout = [(ok,),]

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "150", "SideChangeHappens")