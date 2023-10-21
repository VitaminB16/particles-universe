
def compute_dynamic_scale_and_offset(particles, target_dim, padding=0.0):
    """Compute scale and offset to fit the particles within the target dimensions."""
    min_x, min_y = particles[:, 0].min() - padding, particles[:, 1].min() - padding
    max_x, max_y = particles[:, 0].max() + padding, particles[:, 1].max() + padding
    min_min = min(min_x, min_y)
    max_max = max(max_x, max_y)

    scale_x = target_dim[0] / (max_x - min_x)
    scale_y = target_dim[1] / (max_y - min_y)

    offset_x = -min_x
    offset_y = -min_y

    return scale_x, scale_y, offset_x, offset_y

def lerp(a, b, t=0.05):
    """Linearly interpolate between a and b."""
    return a + t * (b - a)
