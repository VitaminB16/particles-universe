import numpy as np
import matplotlib.pyplot as plt


def universe_game(nParticles, velocity, radius=1, chance_for_global_radius=0.1, beta=1):
    particlePos = np.random.rand(nParticles, 30)
    particlePos[:, 2] *= 360

    fig, ax = plt.subplots()
    scatter = ax.scatter(particlePos[:, 0], particlePos[:, 1], alpha=0.5)
    lines = [ax.plot([0, 0], [0, 0], color="blue")[0] for _ in range(nParticles)]
    i = 0
    while True:
        particlePos[:, 2] = np.mod(particlePos[:, 2], 360)

        direction_angles = np.radians(particlePos[:, 2])
        cos_vals, sin_vals = np.cos(direction_angles), np.sin(direction_angles)

        turns = where_to_turn(
            particlePos[:, :2],
            direction_angles,
            particlePos,
            radius,
            chance_for_global_radius,
        )
        turns = beta * turns
        particlePos[:, 2] = np.mod(particlePos[:, 2] + turns, 360)

        particlePos[:, 0] += velocity * cos_vals
        particlePos[:, 1] += velocity * sin_vals

        scatter.set_offsets(particlePos[:, :2])

        # Update the axis limits
        ax.set_xlim(particlePos[:, 0].min() - 0.1, particlePos[:, 0].max() + 0.1)
        ax.set_ylim(particlePos[:, 1].min() - 0.1, particlePos[:, 1].max() + 0.1)

        plt.pause(0.00001)

    plt.show()


def where_to_turn(
    coords, directions, particlePos, radius, chance_for_global_radius=0.1, beta=1
):
    if np.random.rand() < chance_for_global_radius:
        radius = 10000
    x0s, y0s = coords.T
    bearings = np.mod(
        np.degrees(
            np.arctan2(
                particlePos[:, np.newaxis, 1] - y0s, particlePos[:, np.newaxis, 0] - x0s
            )
            - directions
        ),
        360,
    )
    distances = np.sqrt(
        (particlePos[:, np.newaxis, 0] - x0s) ** 2
        + (particlePos[:, np.newaxis, 1] - y0s) ** 2
    )

    left_mask = (distances < radius) & (bearings < 180)
    right_mask = (distances < radius) & (bearings > 180)

    leftCounter = np.sum(left_mask, axis=0)
    rightCounter = np.sum(right_mask, axis=0)

    return np.sign(leftCounter - rightCounter)


if __name__ == "__main__":
    universe_game(5000, 0.067, radius=5, chance_for_global_radius=0.1, beta=17)
