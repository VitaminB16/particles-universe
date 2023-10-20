import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import time

from .distributions import hexagonal_lattice


class UniverseGame:
    def __init__(self, n_particles, velocity, **kwargs):
        self.n_particles = n_particles
        self.velocity = velocity
        self.radius = kwargs.get("radius", 1)
        self.chance_for_global_radius = kwargs.get("chance_for_global_radius", 0.1)
        self.beta = kwargs.get("beta", 1)
        self.update_interval = kwargs.get("update_interval", 1)
        self.box_width = kwargs.get("box_width", 1)
        self.clip_boundary = kwargs.get("clip_boundary", True)
        self.distribution = kwargs.get("distribution", "uniform")
        self.particlePos = self._initialize_particle_positions()
        self.time_prev = time()

    def _initialize_particle_positions(self):
        if self.distribution == "uniform":
            positions = np.random.rand(self.n_particles, 3) * self.box_width
        elif self.distribution == "hexagonal":
            positions = hexagonal_lattice(
                n_particles=self.n_particles, radius=self.radius
            )
            self.box_width = np.max(positions[:, 0:2])

        positions[:, 2] *= 360
        return positions

    def animate(self, save=False, filename="animation.mp4", fps=60):
        """Display the animation in a matplotlib animation. If save is True, save the animation to filename."""
        fig, ax = self._setup_plot()
        scatter = ax.scatter(self.particlePos[:, 0], self.particlePos[:, 1], alpha=0.5)

        def update(frame):
            self._update_particle_positions(ax)
            scatter.set_offsets(self.particlePos[:, :2])
            self._update_plot_title(ax)

            return (scatter,)

        ani = FuncAnimation(
            fig,
            update,
            frames=None,
            blit=False,
            interval=self.update_interval,
            repeat=True,
        )
        if save:
            ani.save(filename, fps=fps, dpi=300)
        plt.show()

    def _setup_plot(self):
        fig, ax = plt.subplots()
        self._recalculate_limits(ax)
        return fig, ax

    def _update_plot_title(self, ax):
        fps = 1 / (time() - self.time_prev)
        self.time_prev = time()
        ax.set_title(f"FPS: {fps:.2f}")

    def _update_particle_positions(self, ax):
        self._move_particles_based_on_angle()
        if self.clip_boundary:
            self._handle_boundary()
        else:
            self._recalculate_limits(ax)
        turns = self._calculate_turns()
        self._apply_turns(turns)

    def _move_particles_based_on_angle(self):
        direction_angles = np.radians(self.particlePos[:, 2])
        cos_vals, sin_vals = np.cos(direction_angles), np.sin(direction_angles)
        self.particlePos[:, 0] += self.velocity * cos_vals
        self.particlePos[:, 1] += self.velocity * sin_vals

    def _calculate_turns(self):
        effective_radius = self._get_effective_radius()
        dx, dy, distances = self._calculate_relative_distances()
        relative_bearings = self._calculate_relative_bearings(dx, dy)
        direction_turn = self._determine_turn_direction(
            distances, relative_bearings, effective_radius
        )
        return direction_turn

    def _get_effective_radius(self, global_radius=1000):
        global_radius_mask = (
            np.random.rand(self.n_particles) < self.chance_for_global_radius
        )
        return np.where(global_radius_mask, global_radius, self.radius)

    def _calculate_relative_distances(self):
        dx = self.particlePos[:, np.newaxis, 0] - self.particlePos[:, 0]
        dy = self.particlePos[:, np.newaxis, 1] - self.particlePos[:, 1]
        distances = np.sqrt(dx**2 + dy**2)
        return dx, dy, distances

    def _calculate_relative_bearings(self, dx, dy):
        bearings = np.arctan2(dy, dx)
        relative_bearings = np.degrees(bearings) - self.particlePos[:, 2, np.newaxis]
        return (relative_bearings + 180) % 360 - 180

    def _determine_turn_direction(self, distances, relative_bearings, effective_radius):
        left_mask, right_mask = self._get_turn_masks(
            distances, relative_bearings, effective_radius
        )
        leftCounter = left_mask.sum(axis=1)
        rightCounter = right_mask.sum(axis=1)
        direction_turn = np.sign(leftCounter - rightCounter)
        no_neighbors = (leftCounter == 0) & (rightCounter == 0)
        direction_turn[no_neighbors] = np.random.uniform(
            -180, 180, size=no_neighbors.sum()
        )
        return direction_turn

    def _get_turn_masks(self, distances, relative_bearings, effective_radius):
        within_radius = distances < effective_radius[:, np.newaxis]
        left_mask = within_radius & (relative_bearings <= 0)
        right_mask = within_radius & (relative_bearings > 0)
        return left_mask, right_mask

    def _apply_turns(self, turns):
        self.particlePos[:, 2] = np.mod(self.particlePos[:, 2] + turns * self.beta, 360)

    def _handle_boundary(self):
        self._reflect_off_boundaries()
        self.particlePos[:, 2] = np.mod(self.particlePos[:, 2], 360)

    def _reflect_off_boundaries(self):
        conditions = [
            (self.particlePos[:, 0] < 0, 180),
            (self.particlePos[:, 0] > self.box_width, 180),
            (self.particlePos[:, 1] > self.box_width, 360),
            (self.particlePos[:, 1] < 0, 360),
        ]
        for condition, angle in conditions:
            self.particlePos[condition, 2] = angle - self.particlePos[condition, 2]

    def _recalculate_limits(self, ax):
        ax.set_xlim(self.particlePos[:, 0].min(), self.particlePos[:, 0].max())
        ax.set_ylim(self.particlePos[:, 1].min(), self.particlePos[:, 1].max())
