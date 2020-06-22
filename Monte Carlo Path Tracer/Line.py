import pygame as py

class Line:

    def __init__(self, x1, y1, x2, y2, specular = False, transparent = False):
        self.a = [x1, y1]
        self.b = [x2, y2]
        self.specular = specular
        self.transparent = transparent

    def draw(self, window):
        if self.specular:
            py.draw.line(window, (0, 0, 255), self.a, self.b, 2)
        elif self.transparent:
            py.draw.line(window, (255, 255, 255), self.a, self.b, 2)
        else:
            py.draw.line(window, (0, 255, 0), self.a, self.b, 2)

    def checkIntersection(self, line):
        x1 = line.a[0]
        y1 = line.a[1]
        x2 = line.b[0]
        y2 = line.b[1]

        x3 = self.a[0]
        y3 = self.a[1]
        x4 = self.b[0]
        y4 = self.b[1]

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

        if 1 > t > 0 and 1 > u > 0:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            intersection = [x, y]
            return intersection
        else:
            return None