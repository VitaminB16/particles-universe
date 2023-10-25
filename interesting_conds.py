import sys
from universe_game import UniverseGame

conds = {
    "swarm": {
        "n_particles": 1000,
        "velocity": 0.01,
        "radius": 2,
        "chance_for_global_radius": 0.0,
        "beta": 1,
        "box_width": 5,
        "clip_boundary": True,
        "update_interval": 50,
        "distribution": "uniform",
        "draw_trails": True,
    },
    "uninteracting": {
        "n_particles": 100,
        "velocity": 0.01,
        "radius": 2,
        "chance_for_global_radius": 0.0,
        "beta": 0,
        "box_width": 5,
        "clip_boundary": True,
        "update_interval": 50,
        "distribution": "uniform",
        "draw_trails": False,
    },
    "petri_dish": {
        "n_particles": 1000,
        "velocity": 10,
        "radius": 80,
        "chance_for_global_radius": 0.0,
        "beta": 10,
        "box_width": 4000,
        "clip_boundary": True,
        "update_interval": 50,
        "distribution": "uniform",
        "draw_trails": False,
    },
    "shedding_ring": {
        "n_particles": 1000,
        "velocity": 1,
        "radius": 4,
        "chance_for_global_radius": 0.99,
        "beta": 0.2,
        "box_width": 1400,
        "initial_range": 5,
        "clip_boundary": True,
        "update_interval": 50,
        "distribution": "uniform",
        "draw_trails": False,
    },
    "stable_ring_collapse": {
        "n_particles": 1000,
        "velocity": 1,
        "radius": 4,
        "chance_for_global_radius": 1,
        "beta": 0.2,
        "box_width": 1400,
        "initial_range": 1,
        "clip_boundary": True,
        "update_interval": 50,
        "distribution": "uniform",
        "draw_trails": False,
    },
    "pulse_ring": {
        "n_particles": 1000,
        "velocity": 10,
        "radius": 4,
        "chance_for_global_radius": 1,
        "beta": 0,
        "box_width": 1000,
        "clip_boundary": True,
        "initial_range": 0,
        "update_interval": 50,
        "distribution": "uniform",
        "draw_trails": True,
    },
    "galaxy": {
        "n_particles": 1000,
        "velocity": 0.4,
        "radius": 2,
        "beta": 2,
        "alpha": 180,
        "animation_speed": 2,
        "clip_boundary": False,
        "box_width": 5,
        "update_interval": 50,
        "distribution": "uniform",
    },
    "implosion_explosion": {
        "n_particles": 1000,
        "velocity": 0.1,
        "radius": 5,
        "beta": 180,
        "alpha": 180,
        "animation_speed": 2,
        "change_direction_chance": 0.6,
        "clip_boundary": False,
        "box_width": 10,
        "update_interval": 50,
        "distribution": "uniform",
    },
    "onion": {
        "n_particles": 1000,
        "velocity": 0.1,
        "radius": 5,
        "beta": 90,
        "alpha": 180,
        "animation_speed": 2,
        "clip_boundary": False,
        "box_width": 10,
        "update_interval": 50,
        "distribution": "uniform",
    },
}

if __name__ == "__main__":
    args = sys.argv[1:]
    game_kwargs = {}
    if not args:
        print("Usage: python interesting_kwargs.py <condition>")
        print("Available conditions:")
        for key in conds:
            print(f"    {key}")
        sys.exit(1)
    condition = args[0]
    if condition not in conds:
        print(f"Condition {condition} not found.")
        sys.exit(1)
    if "save" in args:
        game_kwargs["save"] = True
        game_kwargs["filename"] = f"{condition}2.mp4"
        args = [arg for arg in args if arg != "save"]
    if len(args) > 1:
        n_particles = int(args[1])
        conds[condition]["n_particles"] = n_particles
    print(f"Condition {condition}:")
    for key, value in conds[condition].items():
        print(f"    {key}: {value}")
    game = UniverseGame(**conds[condition])
    game.start(mode="pygame", **game_kwargs)
