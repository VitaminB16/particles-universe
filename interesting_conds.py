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
}

if __name__ == "__main__":
    args = sys.argv[1:]
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
    if len(args) > 1:
        n_particles = int(args[1])
        conds[condition]["n_particles"] = n_particles
    print(f"Condition {condition}:")
    for key, value in conds[condition].items():
        print(f"    {key}: {value}")
    game = UniverseGame(**conds[condition])
    game.start(mode="pygame")
