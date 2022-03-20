from ..Remainder import Remainder


class EventStart(Remainder):

    def __init__(self, via) -> None:
        super().__init__(via, "100", "EventStart")