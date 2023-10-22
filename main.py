from universe_game import UniverseGame

if __name__ == "__main__":
    game = UniverseGame(
        n_particles=100,
        velocity=0.01,
        radius=2,
        chance_for_global_radius=0.,
        beta=0,
        box_width=5,
        clip_boundary=True,
        update_interval=50,
        distribution="uniform",
        draw_trails=False,
    )
    # game.animate(save=False, filename="animation.mp4", fps=60)
    game.start_pygame()
