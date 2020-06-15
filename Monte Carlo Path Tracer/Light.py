import pygame as py

class LightSource:

    def __init__(self, x, y, color):
        self.pos = [x, y]
        self.color = color

    def draw(self, window):
        py.draw.circle(window, (255, 255, 255), self.pos, 2)