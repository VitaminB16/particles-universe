from .particle import ParticleManager
from .graphics import GraphicsRenderer


class GameController:
    """Class that manages the game loop and the interaction between the particle manager and the renderer"""

    def __init__(self, **kwargs):
        self.pm = ParticleManager(**kwargs)
        self.renderer = GraphicsRenderer(self.pm, **kwargs)

    def start(self, mode="pygame"):
        if mode == "pygame":
            self.renderer.start_pygame()
        elif mode == "matplotlib":
            self.renderer.start_matplotlib()
