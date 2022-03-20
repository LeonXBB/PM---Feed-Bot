from ..Remainder import Remainder


class SideChangeHappens(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "150", "SideChangeHappens")