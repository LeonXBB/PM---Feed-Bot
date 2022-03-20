from ..Remainder import Remainder


class PeriodAboutToStart(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "112", "PeriodAboutToStart")