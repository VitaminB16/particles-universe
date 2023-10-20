import numpy as np


def hexagonal_lattice(n_particles, radius):
    """Return the positions of particles in a uniform hexagonal lattice."""
    vertical_spacing = radius * np.sqrt(3) / 2
    horizontal_spacing = radius

    # A list to store positions
    positions = []

    row_num = 0
    particle_count = 0

    while particle_count < n_particles:
        # Calculate y position based on row number
        y = row_num * vertical_spacing

        # Adjust the starting x position for every other row
        if row_num % 2 == 0:
            x_start = 0
        else:
            x_start = radius / 2

        x = x_start

        while x <= np.sqrt(n_particles) and particle_count < n_particles:
            positions.append([x, y, 0])
            x += horizontal_spacing
            particle_count += 1

        row_num += 1

    return np.array(positions)
