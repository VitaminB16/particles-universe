from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from time import time
import numexpr as ne
import numpy as np
import pygame
import math

from .utils import jprint
from .distributions import hexagonal_lattice
from .pygame_utils import compute_dynamic_scale_and_offset, lerp


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
        self.draw_radius = kwargs.get("draw_radius", False)
        self.draw_trails = kwargs.get("draw_trails", False)
        self.particlePos = self._initialize_particle_positions()
        self.prev_scale_x, self.prev_scale_y = 800/self.box_width, 800/self.box_width
        self.prev_offset_x, self.prev_offset_y = 0, 0
        self.time_prev = time()
        self.window_smooth = 0 if self.clip_boundary else 0.05

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

    def start_pygame(self, window_size=(800, 800)):
        pygame.init()
        screen = pygame.display.set_mode(window_size)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 30)
        lerp_factor = 0.05  # This determines how smooth the transition will be
        circle_radius = 5
        # Create a separate surface for particles
        particle_surface = pygame.Surface(window_size, pygame.SRCALPHA)
        # Precompute x and y velocities for all particles
        velocities = []
        for _, _, angle in self.particlePos:
            radian = math.radians(angle)
            vel_x = self.velocity * math.cos(radian)
            vel_y = self.velocity * math.sin(radian)
            velocities.append((vel_x, vel_y))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            screen.fill((255, 255, 255))  # Fill screen with white
            if self.draw_trails:
                fade_alpha = 5  # Adjust this value to control the rate of fading; smaller values create longer trails
                fade_surface = pygame.Surface(window_size, pygame.SRCALPHA)
                fade_surface.fill((255, 255, 255, fade_alpha))
                particle_surface.blit(fade_surface, (0, 0))
            else:
                particle_surface.fill((0, 0, 0, 0))  # Clear particle surface

            self._update_particle_positions()

            scale_x, scale_y, offset_x, offset_y = compute_dynamic_scale_and_offset(
                self.particlePos, window_size, padding=0.2
            )

            final_scale_x = lerp(self.prev_scale_x, scale_x, self.window_smooth)
            final_scale_y = lerp(self.prev_scale_y, scale_y, self.window_smooth)
            final_offset_x = lerp(self.prev_offset_x, offset_x, self.window_smooth)
            final_offset_y = lerp(self.prev_offset_y, offset_y, self.window_smooth)

            # Update particle positions based on precomputed velocities
            for idx, particle in enumerate(self.particlePos):
                x, y, _ = particle
                vel_x, vel_y = velocities[idx]
                x += vel_x
                y += vel_y
                scaled_x = (x + final_offset_x) * final_scale_x
                scaled_y = (y + final_offset_y) * final_scale_y
                pygame.draw.circle(
                    particle_surface,
                    (0, 0, 0),
                    (scaled_x, scaled_y),
                    circle_radius,
                )
                if self.draw_radius:
                    pygame.draw.circle(
                        particle_surface,
                        (0, 0, 0),
                        (scaled_x, scaled_y),
                        self.radius * max(final_scale_x, final_scale_y),
                        1,
                    )

            screen.blit(particle_surface, (0, 0))

            # Update previous values for next frame
            self.prev_scale_x, self.prev_scale_y = final_scale_x, final_scale_y
            self.prev_offset_x, self.prev_offset_y = final_offset_x, final_offset_y

            # Render the FPS and blit it onto the screen
            fps_text = font.render(f"FPS: {clock.get_fps():.2f}", True, (0, 0, 0))
            screen.blit(fps_text, (10, 10))

            pygame.display.flip()
            clock.tick(120)

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

    def _update_particle_positions(self, ax=None):
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
        effective_radius_sq = self._get_effective_radius_sq()
        dx, dy, distances_sq = self._calculate_relative_distances()
        relative_bearings = self._calculate_relative_bearings(dx, dy)
        direction_turn = self._determine_turn_direction(
            distances_sq, relative_bearings, effective_radius_sq
        )
        return direction_turn

    def _get_effective_radius_sq(self, global_radius_sq=1000**2):
        global_radius_mask = (
            np.random.rand(self.n_particles) < self.chance_for_global_radius
        )
        return np.where(global_radius_mask, global_radius_sq, self.radius**2)

    def _calculate_relative_distances(self):
        x = self.particlePos[:, 0]
        y = self.particlePos[:, 1]
        x_newaxis = x[:, np.newaxis]
        y_newaxis = y[:, np.newaxis]
        dx = ne.evaluate("x_newaxis - x")
        dy = ne.evaluate("y_newaxis - y")
        distances = ne.evaluate("dx**2 + dy**2")
        return dx, dy, distances

    def _calculate_relative_bearings(self, dx, dy):
        bearings = ne.evaluate("arctan2(dy, dx)")
        degrees_conversion_factor = 180 / np.pi
        particle_angles = self.particlePos[:, 2, np.newaxis]
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
        no_neighbors = left_counter + right_counter == 1
        direction_turn[no_neighbors] = np.random.uniform(
            -180, 180, size=no_neighbors.sum()
        )
        return direction_turn

    def _get_turn_masks(self, distances_sq, relative_bearings, effective_radius_sq):
        effective_radius_sq_newaxis = effective_radius_sq[:, np.newaxis]
        within_radius = ne.evaluate("distances_sq < effective_radius_sq_newaxis")
        left_mask = ne.evaluate("within_radius & (relative_bearings <= 0)")
        right_mask = ne.evaluate("within_radius & (relative_bearings > 0)")
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
        if ax is None:
            return
        x_low = np.percentile(self.particlePos[:, 0], 0.03) - self.radius
        x_high = np.percentile(self.particlePos[:, 0], 0.97) + self.radius
        y_low = np.percentile(self.particlePos[:, 1], 0.03) - self.radius
        y_high = np.percentile(self.particlePos[:, 1], 0.97) + self.radius
        ax.set_xlim(x_low, x_high)
        ax.set_ylim(y_low, y_high)
