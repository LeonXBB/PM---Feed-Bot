from ..Remainder import Remainder


class EventAboutToStart(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "102", "EventAboutToStart")