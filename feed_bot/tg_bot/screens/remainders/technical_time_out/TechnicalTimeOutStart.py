from ..Remainder import Remainder


class TechnicalTimeOutStart(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "130", "TechnicalTimeOutStart")