import numpy as np

def compute_dynamic_scale_and_offset(particles, target_dim, padding=0.0):
    """Compute scale and offset to fit the particles within the target dimensions."""
    min_x = np.percentile(particles[:, 0], 3)
    min_y = np.percentile(particles[:, 1], 3)
    max_x = np.percentile(particles[:, 0], 97)
    max_y = np.percentile(particles[:, 1], 97)

    padding = padding * (max(max_x - min_x, max_y - min_y))
    min_x -= padding
    min_y -= padding
    max_x += padding
    max_y += padding

    scale_x = target_dim[0] / (max_x - min_x)
    scale_y = target_dim[1] / (max_y - min_y)

    offset_x = -min_x
    offset_y = -min_y

    return scale_x, scale_y, offset_x, offset_y

def lerp(a, b, t=0.05):
    """Linearly interpolate between a and b."""
    return a + t * (b - a)
