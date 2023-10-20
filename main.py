import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import time


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
    """Simulate a universe of particles moving around in a box"""
    time_prev = time()
    particlePos = np.random.rand(n_particles, 3)
    particlePos[:, 2] *= 360
    particlePos[:, 0:2] *= box_width

    fig, ax = plt.subplots()
    scatter = ax.scatter(particlePos[:, 0], particlePos[:, 1], alpha=0.5)
    ax.set_xlim(0, box_width)
    ax.set_ylim(0, box_width)

    def update(frame):
        nonlocal particlePos, time_prev, ax
        direction_angles = np.radians(particlePos[:, 2])
        cos_vals, sin_vals = np.cos(direction_angles), np.sin(direction_angles)
        turns = where_to_turn(particlePos, radius, chance_for_global_radius)
        particlePos[:, 2] = np.mod(particlePos[:, 2] + turns * beta, 360)

        particlePos[:, 0] += velocity * cos_vals
        particlePos[:, 1] += velocity * sin_vals

        if clip_boundary:
            particlePos = handle_boundary(particlePos, box_width)
        else:
            set_axes_limits(ax, particlePos)

        scatter.set_offsets(particlePos[:, :2])

        time_now = time()
        fps = 1 / (time_now - time_prev)
        time_prev = time_now
        ax.set_title(f"FPS: {fps:.2f}")

        return (scatter,)

    ani = FuncAnimation(
        fig, update, frames=None, blit=False, interval=update_interval, repeat=True
    )
    plt.show()


def where_to_turn(particlePos, radius, chance_for_global_radius=0.1):
    """Calculate the direction to turn for each particle based on the number of neighbors within the radius"""
    n_particles = particlePos.shape[0]
    global_radius_mask = np.random.rand(n_particles) < chance_for_global_radius
    effective_radius = np.where(global_radius_mask, 1000, radius)

    dx = particlePos[:, np.newaxis, 0] - particlePos[:, 0]
    dy = particlePos[:, np.newaxis, 1] - particlePos[:, 1]
    distances = np.sqrt(dx**2 + dy**2)
    within_radius = distances < effective_radius[:, np.newaxis]

    bearings = np.arctan2(dy, dx)
    relative_bearings = np.degrees(bearings) - particlePos[:, 2, np.newaxis]
    relative_bearings = (relative_bearings + 180) % 360 - 180
    left_mask = within_radius & (relative_bearings <= 0)
    right_mask = within_radius & (relative_bearings > 0)

    leftCounter = left_mask.sum(axis=1)
    rightCounter = right_mask.sum(axis=1)
    direction_turn = np.sign(leftCounter - rightCounter)
    no_neighbors = (leftCounter == 0) & (rightCounter == 0)
    direction_turn[no_neighbors] = np.random.uniform(-180, 180, size=no_neighbors.sum())
    return direction_turn


def handle_boundary(particlePos, box_width):
    """Handle boundary conditions for particles that go out of the box"""
    left_bounce = particlePos[:, 0] < 0
    right_bounce = particlePos[:, 0] > box_width
    top_bounce = particlePos[:, 1] > box_width
    bottom_bounce = particlePos[:, 1] < 0

    particlePos[left_bounce, 2] = 180 - particlePos[left_bounce, 2]
    particlePos[right_bounce, 2] = 180 - particlePos[right_bounce, 2]
    particlePos[top_bounce, 2] = 360 - particlePos[top_bounce, 2]
    particlePos[bottom_bounce, 2] = 360 - particlePos[bottom_bounce, 2]
    particlePos[:, 2] = np.mod(particlePos[:, 2], 360)
    return particlePos


def set_axes_limits(ax, particlePos):
    """Set the axes limits to the minimum and maximum particle positions"""
    ax.set_xlim(particlePos[:, 0].min(), particlePos[:, 0].max())
    ax.set_ylim(particlePos[:, 1].min(), particlePos[:, 1].max())


if __name__ == "__main__":
    universe_game(
        n_particles=1000,
        velocity=0.01,
        radius=1,
        chance_for_global_radius=0.4,
        beta=5,
        box_width=5,
        clip_boundary=False,
        update_interval=50,
    )
