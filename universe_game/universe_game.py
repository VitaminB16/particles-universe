import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import time


class UniverseGame:
    def __init__(
        self,
        n_particles,
        velocity,
        radius=1,
        chance_for_global_radius=0.1,
        beta=1,
        update_interval=1,
        box_width=1,
        clip_boundary=True,
    ):
        self.n_particles = n_particles
        self.velocity = velocity
        self.radius = radius
        self.chance_for_global_radius = chance_for_global_radius
        self.beta = beta
        self.update_interval = update_interval
        self.box_width = box_width
        self.clip_boundary = clip_boundary

        self.particlePos = np.random.rand(n_particles, 3)
        self.particlePos[:, 2] *= 360
        self.particlePos[:, 0:2] *= box_width

        self.time_prev = time()

    def animate(self):
        fig, ax = plt.subplots()
        scatter = ax.scatter(self.particlePos[:, 0], self.particlePos[:, 1], alpha=0.5)
        ax.set_xlim(0, self.box_width)
        ax.set_ylim(0, self.box_width)

        def update(frame):
            nonlocal scatter, ax
            self._update_particle_positions()
            scatter.set_offsets(self.particlePos[:, :2])

            fps = 1 / (time() - self.time_prev)
            self.time_prev = time()
            ax.set_title(f"FPS: {fps:.2f}")

            return (scatter,)

        ani = FuncAnimation(
            fig,
            update,
            frames=None,
            blit=False,
            interval=self.update_interval,
            repeat=True,
        )
        plt.show()

    def _update_particle_positions(self):
        direction_angles = np.radians(self.particlePos[:, 2])
        cos_vals, sin_vals = np.cos(direction_angles), np.sin(direction_angles)
        turns = self._where_to_turn()
        self.particlePos[:, 2] = np.mod(self.particlePos[:, 2] + turns * self.beta, 360)

        self.particlePos[:, 0] += self.velocity * cos_vals
        self.particlePos[:, 1] += self.velocity * sin_vals

        if self.clip_boundary:
            self.particlePos = self._handle_boundary()

    def _where_to_turn(self):
        n_particles = self.particlePos.shape[0]
        global_radius_mask = np.random.rand(n_particles) < self.chance_for_global_radius
        effective_radius = np.where(global_radius_mask, 1000, self.radius)

        dx = self.particlePos[:, np.newaxis, 0] - self.particlePos[:, 0]
        dy = self.particlePos[:, np.newaxis, 1] - self.particlePos[:, 1]
        distances = np.sqrt(dx**2 + dy**2)
        within_radius = distances < effective_radius[:, np.newaxis]

        bearings = np.arctan2(dy, dx)
        relative_bearings = np.degrees(bearings) - self.particlePos[:, 2, np.newaxis]
        relative_bearings = (relative_bearings + 180) % 360 - 180
        left_mask = within_radius & (relative_bearings <= 0)
        right_mask = within_radius & (relative_bearings > 0)

        leftCounter = left_mask.sum(axis=1)
        rightCounter = right_mask.sum(axis=1)
        direction_turn = np.sign(leftCounter - rightCounter)
        no_neighbors = (leftCounter == 0) & (rightCounter == 0)
        direction_turn[no_neighbors] = np.random.uniform(
            -180, 180, size=no_neighbors.sum()
        )
        return direction_turn

    def _handle_boundary(self):
        left_bounce = self.particlePos[:, 0] < 0
        right_bounce = self.particlePos[:, 0] > self.box_width
        top_bounce = self.particlePos[:, 1] > self.box_width
        bottom_bounce = self.particlePos[:, 1] < 0

        self.particlePos[left_bounce, 2] = 180 - self.particlePos[left_bounce, 2]
        self.particlePos[right_bounce, 2] = 180 - self.particlePos[right_bounce, 2]
        self.particlePos[top_bounce, 2] = 360 - self.particlePos[top_bounce, 2]
        self.particlePos[bottom_bounce, 2] = 360 - self.particlePos[bottom_bounce, 2]
        self.particlePos[:, 2] = np.mod(self.particlePos[:, 2], 360)
        return self.particlePos
