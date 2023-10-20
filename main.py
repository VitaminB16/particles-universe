"""
Universe particle simulation, after Thomas Schmickl and Martin Stefanec of University of Graz, Austria.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist


def universe_game(nParticles, velocity):
    global radius, particlePos

    v = velocity
    radius = 1
    particlePos = np.random.rand(nParticles, 3)
    particlePos[:, 2] *= 360

    plt.scatter(particlePos[:, 0], particlePos[:, 1])

    p = 0
    while True:
        p += 1
        particlePos[:, 2] = np.mod(particlePos[:, 2], 360)

        for j in range(nParticles):
            coord = particlePos[j, :2]
            direction = particlePos[j, 2]
            particlePos[j, 2] = np.mod(direction + where_to_turn(coord, direction), 360)

        particlePos[:, 0] += v * np.cos(np.radians(particlePos[:, 2]))
        particlePos[:, 1] += v * np.sin(np.radians(particlePos[:, 2]))
        plt.scatter(particlePos[:, 0], particlePos[:, 1])

        plt.title(f"{p}")
        plt.pause(0.001)
        plt.clf()

    return particlePos


def where_to_turn(coord, direction):
    global particlePos

    x0, y0 = coord
    leftCounter, rightCounter = 0, 0

    for i in range(len(particlePos)):
        x1, y1 = particlePos[i, :2]
        bearing = np.degrees(np.arctan2(y1 - y0, x1 - x0))
        bearing = np.mod(bearing - direction, 360)

        if (pdist(np.array([[x0, y0], [x1, y1]])) < radius) and bearing < 180:
            leftCounter += 1
        elif (pdist(np.array([[x0, y0], [x1, y1]])) < radius) and bearing > 180:
            rightCounter += 1

    return np.sign(leftCounter - rightCounter)


if __name__ == "__main__":
    universe_game(100, 0.05)
