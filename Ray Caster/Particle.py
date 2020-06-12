from numpy import deg2rad
from Ray import *

class Particle:

    def __init__(self, x, y):
        self.pos = [x, y]
        self.rays = []
        for a in range(0, 360, 1):
            self.rays.append(Ray(self.pos, deg2rad(a)))

    def draw(self, window):
        py.draw.circle(window, (255, 255, 255), self.pos, 1, 1)
        for ray in self.rays:
            ray.draw(window)

    def castRays(self, window, boundaries):
         for ray in self.rays:
            record = 1000000
            closest = None
            for line in boundaries:
                point = ray.cast(line)
                if point is not None:
                    dis = point[2]
                    if dis < record:
                        record = dis
                        closest = point[:2]
            if closest is not None:
                py.draw.line(window, (255, 255, 255), self.pos, closest, 1)