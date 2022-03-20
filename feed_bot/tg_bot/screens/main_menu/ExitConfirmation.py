from ..Screen import Screen


class ExitConfirmation(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "12", "ExitConfirmation")