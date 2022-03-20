from ..Remainder import Remainder


class TimeOutStart(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "120", "TimeOutStart")