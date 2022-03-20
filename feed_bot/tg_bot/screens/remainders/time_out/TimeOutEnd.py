from ..Remainder import Remainder


class TimeOutEnd(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "121", "TimeOutStart")