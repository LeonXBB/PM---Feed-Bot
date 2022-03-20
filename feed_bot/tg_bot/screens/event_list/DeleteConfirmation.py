from ..Screen import Screen


class DeleteConfirmation(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "42", "DeleteConfirmation")