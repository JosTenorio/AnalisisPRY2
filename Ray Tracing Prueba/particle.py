from numpy import deg2rad
from ray import *


class Particle:
    def __init__(self):
        self.pos = array([250, 250])

    def display(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.pos, 1, 1)

        for ray in self.rays:
            ray.display(screen)

    def look(self, screen, walls):
        self.rays = []
        for i in range(0, 360, 4):
            self.rays.append(Ray(self.pos[0], self.pos[1], deg2rad(i)))


        for ray in self.rays:
            closest = 10000000
            closestpt = None

            ray.lookAt(100+i,100+i)
            i += 2

            for wall in walls:
                pt = ray.cast(wall)

                if pt is not None:
                    dis = linalg.norm(pt - self.pos)
                    if (dis < closest):
                        closest = dis
                        closestpt = pt

            if closestpt is not None:
                pygame.draw.line(screen, (255, 255, 255), self.pos, array(closestpt, int), 2)