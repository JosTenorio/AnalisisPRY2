import sys
from Line import *
from Particle import *

WIDTH = 800
HEIGHT = 800
RUNNING = True

py.init()
WINDOW = py.display.set_mode([WIDTH, HEIGHT])

class Display:

    def __init__(self):
        self.boundaries = []
        self.particle = Particle(0, 0)
        self.clock = py.time.Clock()

    def createBoundaries(self):
        # outer border
        self.boundaries.append(Line(0, 0, WIDTH, 0))
        self.boundaries.append(Line(0, 0, 0, HEIGHT))
        self.boundaries.append(Line(0, HEIGHT, WIDTH, HEIGHT))
        self.boundaries.append(Line(WIDTH, 0, WIDTH, HEIGHT))
        # random boundaries
        for i in range (4):
            x1 = np.random.randint(0, WIDTH)
            y1 = np.random.randint(0, HEIGHT)
            x2 = np.random.randint(0, WIDTH)
            y2 = np.random.randint(0, HEIGHT)
            wall = Line(x1, y1, x2, y2)
            self.boundaries.append(wall)

    def drawBoundaries(self):
        for line in self.boundaries:
            line.draw(WINDOW)

    def start(self):
        self.createBoundaries()
        while RUNNING:
            WINDOW.fill((0, 0, 0))

            for event in py.event.get():

                if event.type == py.QUIT:
                    sys.exit()

                if event.type == py.MOUSEMOTION:
                    pos = event.pos
                    self.particle.pos[0] = pos[0]
                    self.particle.pos[1] = pos[1]

            self.drawBoundaries()
            self.particle.castRays(WINDOW, self.boundaries)
            py.display.update()
            self.clock.tick(60)

D = Display()
D.start()