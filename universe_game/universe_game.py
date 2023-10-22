from universe_game.managers import GameController


class UniverseGame:
    def __init__(self, **kwargs):
        self.gc = GameController(**kwargs)

    def start(self, mode="pygame"):
        self.gc.start(mode)
