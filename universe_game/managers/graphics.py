import math
import pygame
import numpy as np
from time import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from universe_game.pygame_utils import compute_dynamic_scale_and_offset, lerp


class GraphicsRenderer:
    """
    Class that manages the rendering of the particles and the window.
    Currently supports pygame and matplotlib.
    """

    def __init__(self, particle_manager, **kwargs):
        self.particle_manager = particle_manager
        self.velocity = kwargs.get("velocity", 0.1)
        self.radius = kwargs.get("radius", 1)
        self.clip_boundary = kwargs.get("clip_boundary", True)
        self.update_interval = kwargs.get("update_interval", 1)
        self.draw_radius = kwargs.get("draw_radius", False)
        self.draw_trails = kwargs.get("draw_trails", False)
        self.box_width = kwargs.get("box_width", 5)
        self.particle_pos = self.particle_manager.particle_pos
        self.prev_scale_x, self.prev_scale_y = (
            800 / self.box_width,
            800 / self.box_width,
        )
        self.prev_offset_x, self.prev_offset_y = 0, 0
        self.time_prev = time()
        self.window_smooth = 0 if self.clip_boundary else 0.05

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
        for _, _, angle in self.particle_pos:
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

            self.particle_manager._update_particle_positions()

            scale_x, scale_y, offset_x, offset_y = compute_dynamic_scale_and_offset(
                self.particle_manager.particle_pos, window_size, padding=0.2
            )

            final_scale_x = lerp(self.prev_scale_x, scale_x, self.window_smooth)
            final_scale_y = lerp(self.prev_scale_y, scale_y, self.window_smooth)
            final_offset_x = lerp(self.prev_offset_x, offset_x, self.window_smooth)
            final_offset_y = lerp(self.prev_offset_y, offset_y, self.window_smooth)

            # Update particle positions based on precomputed velocities
            for idx, particle in enumerate(self.particle_manager.particle_pos):
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

    def start_matplotlib(self, save=False, filename="animation.mp4", fps=60):
        """Display the animation in a matplotlib animation. If save is True, save the animation to filename."""
        fig, ax = self._setup_plot()
        scatter = ax.scatter(
            self.particle_manager.particle_pos[:, 0],
            self.particle_manager.particle_pos[:, 1],
            alpha=0.5,
        )

        def update(frame):
            self.particle_manager._update_particle_positions()
            scatter.set_offsets(self.particle_manager.particle_pos[:, :2])
            self._update_plot_title(ax)
            if self.clip_boundary is False:
                self._recalculate_limits(ax)

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

    def _recalculate_limits(self, ax):
        if ax is None:
            return
        x_low = np.percentile(self.particle_manager.particle_pos[:, 0], 3) - self.radius / 2
        x_high = (
            np.percentile(self.particle_manager.particle_pos[:, 0], 97) + self.radius / 2
        )
        y_low = np.percentile(self.particle_manager.particle_pos[:, 1], 3) - self.radius / 2
        y_high = (
            np.percentile(self.particle_manager.particle_pos[:, 1], 97) + self.radius / 2
        )
        ax.set_xlim(x_low, x_high)
        ax.set_ylim(y_low, y_high)
