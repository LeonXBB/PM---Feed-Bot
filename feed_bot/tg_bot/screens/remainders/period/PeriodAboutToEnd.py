from ..Remainder import Remainder


class PeriodAboutToEnd(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "113", "PeriodAboutToEnd")