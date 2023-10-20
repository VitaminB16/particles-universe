import numpy as np
import matplotlib.pyplot as plt


def universe_game(nParticles, velocity, radius=1, chance_for_global_radius=0.1, beta=1):
    particlePos = np.random.rand(nParticles, 3)
    particlePos[:, 2] *= 360

    fig, ax = plt.subplots()
    scatter = ax.scatter(particlePos[:, 0], particlePos[:, 1], alpha=0.5)
    i = 0
    while True:
        particlePos[:, 2] = np.mod(particlePos[:, 2], 360)

        direction_angles = np.radians(particlePos[:, 2])
        cos_vals, sin_vals = np.cos(direction_angles), np.sin(direction_angles)

        turns = where_to_turn(particlePos, radius, chance_for_global_radius)
        turns = beta * turns
        particlePos[:, 2] = np.mod(particlePos[:, 2] + turns, 360)

        particlePos[:, 0] += velocity * cos_vals
        particlePos[:, 1] += velocity * sin_vals

        scatter.set_offsets(particlePos[:, :2])

        ax.set_xlim(particlePos[:, 0].min() - 0.1, particlePos[:, 0].max() + 0.1)
        ax.set_ylim(particlePos[:, 1].min() - 0.1, particlePos[:, 1].max() + 0.1)
        plt.pause(0.001)

        i += 1

    plt.show()


def where_to_turn(particlePos, radius, chance_for_global_radius=0.1):
    if np.random.rand() < chance_for_global_radius:
        radius = 10000
    dx = particlePos[:, np.newaxis, 0] - particlePos[:, 0]
    dy = particlePos[:, np.newaxis, 1] - particlePos[:, 1]
    distances = np.sqrt(dx**2 + dy**2)

    bearings = np.arctan2(dy, dx)
    direction_angles = np.radians(particlePos[:, 2])
    relative_bearings = np.mod(np.degrees(bearings - direction_angles), 360)

    left_mask = (distances < radius) & (relative_bearings < 180)
    right_mask = (distances < radius) & (relative_bearings > 180)

    leftCounter = np.sum(left_mask, axis=0)
    rightCounter = np.sum(right_mask, axis=0)

    return np.sign(leftCounter - rightCounter)


if __name__ == "__main__":
    universe_game(1000, 0.01, radius=1, chance_for_global_radius=0.0, beta=1)
