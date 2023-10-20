import numpy as np
import matplotlib.pyplot as plt


def universe_game(
    n_particles,
    velocity,
    radius=1,
    chance_for_global_radius=0.1,
    beta=1,
    box_width=1,
    clip_boundary=True,
):
    particlePos = np.random.rand(n_particles, 3)
    particlePos[:, 2] *= 360
    x_lim = np.array([0, box_width])
    y_lim = np.array([0, box_width])
    particlePos[:, 0] *= x_lim[1]
    particlePos[:, 1] *= y_lim[1]
    fig, ax = plt.subplots()
    scatter = ax.scatter(particlePos[:, 0], particlePos[:, 1], alpha=0.5)
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    i = 0
    while True:
        direction_angles = np.radians(particlePos[:, 2])
        cos_vals, sin_vals = np.cos(direction_angles), np.sin(direction_angles)

        turns = where_to_turn(particlePos, radius, chance_for_global_radius)
        turns = beta * turns
        particlePos[:, 2] = np.mod(particlePos[:, 2] + turns, 360)

        particlePos[:, 0] += velocity * cos_vals
        particlePos[:, 1] += velocity * sin_vals

        if clip_boundary:
            # Bouncing logic
            left_bounce = particlePos[:, 0] < x_lim[0]
            right_bounce = particlePos[:, 0] > x_lim[1]
            top_bounce = particlePos[:, 1] > y_lim[1]
            bottom_bounce = particlePos[:, 1] < y_lim[0]

            particlePos[left_bounce, 2] = 180 - particlePos[left_bounce, 2]
            particlePos[right_bounce, 2] = 180 - particlePos[right_bounce, 2]
            particlePos[top_bounce, 2] = 360 - particlePos[top_bounce, 2]
            particlePos[bottom_bounce, 2] = 360 - particlePos[bottom_bounce, 2]
            particlePos[:, 2] = np.mod(particlePos[:, 2], 360)
        else:
            x_range = [particlePos[:, 0].min(), particlePos[:, 0].max()]
            y_range = [particlePos[:, 1].min(), particlePos[:, 1].max()]
            ax.set_xlim(x_range)
            ax.set_ylim(y_range)
        scatter.set_offsets(particlePos[:, :2])
        plt.pause(0.0001)

        i += 1

    plt.show()


def where_to_turn(particlePos, radius, chance_for_global_radius=0.1):
    n_particles = particlePos.shape[0]
    global_radius_mask = np.random.rand(n_particles) < chance_for_global_radius
    radius = np.array([radius] * n_particles)
    radius[global_radius_mask] = 1000
    dx = particlePos[:, np.newaxis, 0] - particlePos[:, 0]
    dy = particlePos[:, np.newaxis, 1] - particlePos[:, 1]
    distances = np.sqrt(dx**2 + dy**2)

    bearings = np.arctan2(dy, dx)
    relative_bearings = np.mod(np.degrees(bearings) - particlePos[:, 2], 360)

    left_mask = (distances < radius) & (relative_bearings < 180)
    right_mask = (distances < radius) & (relative_bearings > 180)

    leftCounter = np.sum(left_mask, axis=0)
    rightCounter = np.sum(right_mask, axis=0)

    return np.sign(leftCounter - rightCounter)


if __name__ == "__main__":
    universe_game(
        n_particles=1000,
        velocity=0.4,
        radius=10,
        chance_for_global_radius=0.1,
        beta=1,
        box_width=100,
        clip_boundary=True,
    )
