from universe_game import UniverseGame

if __name__ == "__main__":
    game = UniverseGame(
        n_particles=1000,
        velocity=0.01,
        radius=1,
        chance_for_global_radius=0.4,
        beta=5,
        box_width=5,
        clip_boundary=False,
        update_interval=50,
    )
    game.animate()
