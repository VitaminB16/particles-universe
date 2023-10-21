from universe_game import UniverseGame

if __name__ == "__main__":
    game = UniverseGame(
        n_particles=1000,
        velocity=0.02,
        radius=2,
        chance_for_global_radius=0.,
        beta=0.5,
        box_width=10,
        clip_boundary=False,
        update_interval=50,
        distribution="uniform",
        draw_radius=False,
    )
    # game.animate(save=False, filename="animation.mp4", fps=60)
    game.start_pygame()
