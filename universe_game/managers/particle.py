import numpy as np
import numexpr as ne
from universe_game.distributions import hexagonal_lattice


class ParticleManager:
    def __init__(self, n_particles, velocity, **kwargs):
        self.n_particles = n_particles
        self.velocity = velocity
        self.radius = kwargs.get("radius", 1)
        self.chance_for_global_radius = kwargs.get("chance_for_global_radius", 0.1)
        self.beta = kwargs.get("beta", 1)
        self.box_width = kwargs.get("box_width", 1)
        self.clip_boundary = kwargs.get("clip_boundary", True)
        self.distribution = kwargs.get("distribution", "uniform")
        self.particle_pos = self._initialize_particle_positions()

    def _initialize_particle_positions(self):
        if self.distribution == "uniform":
            positions = np.random.rand(self.n_particles, 3)
            positions[:, 0:2] *= self.box_width
        elif self.distribution == "hexagonal":
            positions = hexagonal_lattice(
                n_particles=self.n_particles, radius=self.radius
            )
            self.box_width = np.max(positions[:, 0:2])

        positions[:, 2] *= 360

        return positions

    def _update_particle_positions(self):
        self._move_particles_based_on_angle()
        if self.clip_boundary:
            self._handle_boundary()
        turns = self._calculate_turns()
        self._apply_turns(turns)

    def _move_particles_based_on_angle(self):
        direction_angles = np.radians(self.particle_pos[:, 2])
        cos_vals, sin_vals = np.cos(direction_angles), np.sin(direction_angles)
        self.particle_pos[:, 0] += self.velocity * cos_vals
        self.particle_pos[:, 1] += self.velocity * sin_vals

    def _calculate_turns(self):
        effective_radius_sq = self._get_effective_radius_sq()
        dx, dy, distances_sq = self._calculate_relative_distances()
        relative_bearings = self._calculate_relative_bearings(dx, dy)
        direction_turn = self._determine_turn_direction(
            distances_sq, relative_bearings, effective_radius_sq
        )
        return direction_turn

    def _get_effective_radius_sq(self, global_radius_sq=1000**2):
        global_radius_sq = self.radius * global_radius_sq
        global_radius_mask = (
            np.random.rand(self.n_particles) < self.chance_for_global_radius
        )
        return np.where(global_radius_mask, global_radius_sq, self.radius**2)

    def _calculate_relative_distances(self):
        x = self.particle_pos[:, 0]
        y = self.particle_pos[:, 1]
        x_newaxis = x[:, np.newaxis]
        y_newaxis = y[:, np.newaxis]
        dx = ne.evaluate("x_newaxis - x")
        dy = ne.evaluate("y_newaxis - y")
        distances = ne.evaluate("dx**2 + dy**2")
        return dx, dy, distances

    def _calculate_relative_bearings(self, dx, dy):
        bearings = ne.evaluate("arctan2(dy, dx)")
        degrees_conversion_factor = 180 / np.pi
        particle_angles = self.particle_pos[:, 2, np.newaxis]
        relative_bearings = ne.evaluate(
            "bearings * degrees_conversion_factor - particle_angles"
        )
        adjusted_relative_bearings = ne.evaluate(
            "(relative_bearings + 180) % 360 - 180"
        )
        return adjusted_relative_bearings

    def _determine_turn_direction(
        self, distances_sq, relative_bearings, effective_radius_sq
    ):
        left_mask, right_mask = self._get_turn_masks(
            distances_sq, relative_bearings, effective_radius_sq
        )
        left_counter = left_mask.sum(axis=1)
        right_counter = right_mask.sum(axis=1)
        direction_turn = np.sign(left_counter - right_counter)
        no_neighbors = left_counter + right_counter == 0
        random_turns = np.random.choice(
            [-90 / self.beta, 90 / self.beta], size=no_neighbors.sum()
        )
        direction_turn[no_neighbors] = random_turns

        return direction_turn

    def _get_turn_masks(self, distances_sq, relative_bearings, effective_radius_sq):
        effective_radius_sq_newaxis = effective_radius_sq[:, np.newaxis]
        within_radius = ne.evaluate(
            "(distances_sq < effective_radius_sq_newaxis) & (distances_sq > 0)"
        )
        left_mask = ne.evaluate("within_radius & (relative_bearings < 0)")
        right_mask = ne.evaluate("within_radius & (relative_bearings > 0)")
        return left_mask, right_mask

    def _apply_turns(self, turns):
        self.particle_pos[:, 2] = np.mod(
            self.particle_pos[:, 2] + turns * self.beta, 360
        )

    def _handle_boundary(self):
        self._reflect_off_boundaries()
        self.particle_pos[:, 2] = np.mod(self.particle_pos[:, 2], 360)

    def _reflect_off_boundaries(self):
        conditions = [
            (self.particle_pos[:, 0] < 0, 180),
            (self.particle_pos[:, 0] > self.box_width, 180),
            (self.particle_pos[:, 1] > self.box_width, 360),
            (self.particle_pos[:, 1] < 0, 360),
        ]

        for condition, angle in conditions:
            self.particle_pos[condition, 2] = angle - self.particle_pos[condition, 2]
