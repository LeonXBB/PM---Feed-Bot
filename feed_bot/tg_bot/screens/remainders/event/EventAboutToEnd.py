from ..Remainder import Remainder


class EventAboutToEnd(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "103", "EventAboutToEnd")