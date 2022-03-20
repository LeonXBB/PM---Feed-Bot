from ..Remainder import Remainder


class EventEnd(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "101", "EventEnd")