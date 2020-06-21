import pygame as py

class LightSource:

    def __init__(self, x1, y1, color, x2 = -1, y2 = -1):
        self.pos = [x1, y1]
        self.a = [x1, y1]
        if x2 == -1 or y2 == -1:
            self.circle = True
            self.b = [x1, y1 + 1]
        else:
            self.circle = False
            self.b = [x2, y2]
        self.color = color

    def draw(self, window):
        if self.circle:
            py.draw.circle(window, [x * 255 for x in self.color], self.pos, 5)
        else:
            py.draw.line(window, [x * 255 for x in self.color], self.a, self.b, 5)