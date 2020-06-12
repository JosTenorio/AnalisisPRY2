import pygame as py

class Line:

    def __init__(self, x1, y1, x2, y2):
        self.a = [x1, y1]
        self.b = [x2, y2]

    def draw(self, window):
        py.draw.line(window, (255, 255, 255), self.a, self.b, 2)