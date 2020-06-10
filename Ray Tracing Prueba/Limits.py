import pygame

class Limits:
    def __init__(self, x1, y1, x2, y2):
        self.a = [x1, y1]
        self.b = [x2, y2]

    def display(self, screen):
        pygame.draw.line(screen, (255, 255, 255), self.a, self.b, 2)