from ..Remainder import Remainder


class PeriodStart(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "110", "PeriodStart")