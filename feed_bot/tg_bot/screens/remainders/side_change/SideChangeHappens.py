from ..Remainder import Remainder


class SideChangeHappens(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        ok = {"text": self.strings[1][0], "data": "r_0_50_0"}

        layout = [(ok,),]

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "150", "SideChangeHappens")