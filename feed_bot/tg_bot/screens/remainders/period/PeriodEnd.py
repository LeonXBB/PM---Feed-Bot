from ..Remainder import Remainder


class PeriodEnd(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "111", "PeriodEnd")