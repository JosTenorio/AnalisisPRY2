import numpy as np
import pygame
import random
from PIL import Image
from Point import *
import rt
import threading


def pathtracing():
    while True:
        # loop through all the pixels, add 0.1 to avoid division by 0 <- temporal
        for x in range(500):
            for y in range(500):
                point = Point(x + 0.1, y + 0.1)
                # pixel color
                pixel = 0
                for source in sources:
                    # calculates direction to light source
                    dir = source - point
                    # warning check (0, 0)

                    # distance between point and light source
                    length = rt.length(dir)

                    # normalize direction
                    dir = rt.normalize(dir)

                    free = True
                    for seg in segments:
                        # check if ray intersects with segment
                        dist = rt.raySegmentIntersect(point, dir, seg[0], seg[1])
                        # if intersection, or if intersection is closer than light source
                        if dist != -1 and dist < length:
                            free = False
                            break

                    if free:
                        intensity = (1 - (length / 500)) ** 2
                        values = (ref[int(point.y)][int(point.x)])[:3]
                        # combine color, light source and light color
                        values = values * intensity * light

                        # add all light sources
                        pixel += values
                    for sample in numSamples:
                        while True:
                            randomPoint = Point(random.randint(1, 500), random.randint(1, 500))
                            if randomPoint != point:
                                break
                        randomDir = randomPoint - point
                        pixel += tracepath(0, point, dir, False, 0, 0)
                    # average pixel value and assign
                px[int(point.x)][int(point.y)] = pixel // len(sources) + numSamples

def tracepath (depth, point, dir, values, distance):
    color = 0
    if depth > bouncingDepth:
        return 0
    length = rt.length(dir)
    dir = rt.normalize(dir)
    # CHECK IF DIR HITS A LIGHT SOURCE
    lightSource = random.randint(0,1)
    if lightSource:
        if depth == 0:
            return 0
        #ADD DISTANCE TO LIGHT SOURCE TO DISTANCE
        intensity = (1 - (distance / 500)) ** 2
        return values * intensity * light
    #CHECK IF DIR HITS A SEGMENT
    hitSegment = random.randint(0, 1)
    if hitSegment:
        #IF IT DOES, CREATE A NEW DIRECTION AND MODIFY VALUES AND DISTANCE
        return tracepath (depth+1, point, dir, values, distance)
    return 0

# pygame init
h, w = 500, 500
pygame.init()
window = pygame.display.set_mode((w, h))
pygame.display.set_caption("2D Raytracing")
done = False
clock = pygame.time.Clock()

# init random
random.seed()

# image setup
img = Image.new("RGB", (500, 500), (0, 0, 0))
px = np.array(img)

# reference image for background color
im_file = Image.open("fondo.png")
ref = np.array(im_file)

# light positions
sources = [Point(195, 200), Point(294, 200)]

# light color
light = np.array([1, 1, 0.75])

# warning, point order affects intersection test!!
segments = [
    ([Point(180, 135), Point(215, 135)]),
    ([Point(285, 135), Point(320, 135)]),
    ([Point(320, 135), Point(320, 280)]),
    ([Point(320, 320), Point(320, 355)]),
    ([Point(320, 355), Point(215, 355)]),
    ([Point(180, 390), Point(180, 286)]),
    ([Point(180, 286), Point(140, 286)]),
    ([Point(320, 320), Point(360, 320)]),
    ([Point(180, 250), Point(180, 135)]),
]
#Montecarlo parameters
numSamples = 500
bouncingDepth = 2


# thread setup
t = threading.Thread(target=pathtracing(), daemon=True)
t.start()

# main loop
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Clear screen to white before drawing
    window.fill((255, 255, 255))

    # Convert to a surface and splat onto screen
    surface = pygame.surfarray.make_surface(px)
    window.blit(surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)
