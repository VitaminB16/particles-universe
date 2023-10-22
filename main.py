from universe_game import UniverseGame
import sys

sys.path.append("..")

if __name__ == "__main__":
    game = UniverseGame(
        n_particles=800,
        velocity=0.08,
        radius=3,
        chance_for_global_radius=0.2,
        beta=1,
        box_width=50,
        clip_boundary=False,
        update_interval=50,
        distribution="uniform",
        draw_trails=False,
        draw_radius=False,
    )
    # game.animate(save=False, filename="animation.mp4", fps=60)
    game.start(mode="pygame")
