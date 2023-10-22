from universe_game import UniverseGame
from initial_conditions import conds
import sys

sys.path.append("..")

if __name__ == "__main__":
    game = UniverseGame(**conds)
    # game.animate(save=False, filename="animation.mp4", fps=60)
    game.start(mode="pygame")
