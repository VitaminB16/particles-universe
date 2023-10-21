from universe_game import UniverseGame

if __name__ == "__main__":
    game = UniverseGame(
        n_particles=1000,
        velocity=0.005,
        radius=5,
        chance_for_global_radius=0.0,
        beta=5,
        box_width=5,
        clip_boundary=False,
        update_interval=50,
        distribution="uniform"
    )
    # game.animate(save=False, filename="animation.mp4", fps=60)
    game.start_pygame()
