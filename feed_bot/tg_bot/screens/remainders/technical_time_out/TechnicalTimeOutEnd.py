from ..Remainder import Remainder


class TechnicalTimeOutEnd(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "131", "TechnicalTimeOutEnd")