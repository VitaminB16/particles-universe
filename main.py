import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def universe_game(
    n_particles,
    velocity,
    radius=1,
    chance_for_global_radius=0.1,
    beta=1,
    update_interval=1,
    box_width=1,
    clip_boundary=True,
):
    particlePos = np.random.rand(n_particles, 3)
    particlePos[:, 2] *= 360
    particlePos[:, 0] *= box_width
    particlePos[:, 1] *= box_width

    fig, ax = plt.subplots()
    scatter = ax.scatter(particlePos[:, 0], particlePos[:, 1], alpha=0.5)
    ax.set_xlim(0, box_width)
    ax.set_ylim(0, box_width)

    def update(frame):
        nonlocal particlePos

        direction_angles = np.radians(particlePos[:, 2])
        cos_vals, sin_vals = np.cos(direction_angles), np.sin(direction_angles)

        turns = where_to_turn(particlePos, radius, chance_for_global_radius)
        turns = beta * turns
        particlePos[:, 2] = np.mod(particlePos[:, 2] + turns, 360)

        particlePos[:, 0] += velocity * cos_vals
        particlePos[:, 1] += velocity * sin_vals

        if clip_boundary:
            # Bouncing logic
            left_bounce = particlePos[:, 0] < 0
            right_bounce = particlePos[:, 0] > box_width
            top_bounce = particlePos[:, 1] > box_width
            bottom_bounce = particlePos[:, 1] < 0

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
        return (scatter,)

    ani = FuncAnimation(
        fig, update, frames=None, blit=False, interval=update_interval, repeat=True
    )
    plt.show()


def where_to_turn(particlePos, radius, chance_for_global_radius=0.1):
    n_particles = particlePos.shape[0]
    global_radius_mask = np.random.rand(n_particles) < chance_for_global_radius
    effective_radius = np.where(global_radius_mask, 1000, radius)

    dx = particlePos[:, np.newaxis, 0] - particlePos[:, 0]
    dy = particlePos[:, np.newaxis, 1] - particlePos[:, 1]
    distances = np.sqrt(dx**2 + dy**2)
    within_radius = distances < effective_radius[:, np.newaxis]

    bearings = np.arctan2(dy, dx)
    relative_bearings = np.mod(
        np.degrees(bearings) - particlePos[:, 2, np.newaxis], 360
    )
    left_mask = within_radius & (relative_bearings < 180)
    right_mask = within_radius & (relative_bearings > 180)

    leftCounter = np.sum(left_mask, axis=0)
    rightCounter = np.sum(right_mask, axis=0)
    direction_turn = np.sign(leftCounter - rightCounter)
    # For particles that don't have any neighbors within the radius, set them to random direction
    no_neighbors = leftCounter + rightCounter <= 2
    direction_turn[no_neighbors] = np.random.uniform(-180, 180, size=no_neighbors.sum())
    return direction_turn


if __name__ == "__main__":
    universe_game(
        n_particles=1000,
        velocity=0.05,
        radius=1,
        chance_for_global_radius=0.1,
        beta=1,
        box_width=10,
        clip_boundary=False,
        update_interval=10,
    )
