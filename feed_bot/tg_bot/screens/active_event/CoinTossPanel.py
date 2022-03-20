from ..Screen import Screen


class CoinTossPanel(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "32", "CoinTossPanel")