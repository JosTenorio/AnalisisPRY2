import pygame as py
import numpy as np

class Ray:

    def __init__(self, x, y, angle):
        self.pos = [x, y]
        radians = np.deg2rad(angle)
        self.dir = [np.cos(radians), np.sin(radians)]

    def draw(self, window):
        py.draw.line(window, (255, 255, 255), self.pos, np.add(self.pos, [x * 500 for x in self.dir]), 1)

    def checkIntersection(self, line):
        x1 = line.a[0]
        y1 = line.a[1]
        x2 = line.b[0]
        y2 = line.b[1]

        x3 = self.pos[0]
        y3 = self.pos[1]
        x4 = self.pos[0] + self.dir[0]
        y4 = self.pos[1] + self.dir[1]

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

        if 1 > t > 0 and u > 0:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            intersection = [x, y, u]
            return intersection
        else:
            return None