import sys
import threading
import random
import math
from PIL import Image
from Line import *
from Light import *
from Ray import *

def renderLight():
    while True:

        # loop through all the pixels
        for x in range (500):
            for y in range (500):

                # pixel color black
                color = 0

                # obtain reference pixel value
                refValue = (referencePixels[y][x])[:3]

                # calculate direct lighting
                for source in lightSources:
                    sourceX = source.pos[0]
                    sourceY = source.pos[1]

                    # create a line segment from pixel to light source
                    directLine = Line(x, y, sourceX, sourceY)

                    # calculate distance from pixel to light source
                    sourceDist = math.sqrt(((x - sourceX) ** 2)+((y - sourceY) ** 2))

                    # check if line segments intersect
                    collision = False
                    for boundary in boundaries:
                        intersection = directLine.checkIntersection(boundary)
                        if intersection is not None:
                            collision = True
                            break

                    if not collision:

                        # calculate light intensity
                        intensity = (1 - (sourceDist / 500)) ** 2

                        # combine color, light source and light color
                        currentValue = refValue * intensity * light

                        # add all light sources
                        color += currentValue

                # calculate indirect lighting with monte carlo
                for i in range (NUM_SAMPLES):

                    # get random direction
                    angle = random.uniform(0, 360)

                    # create ray from pixel to random direction
                    ray = Ray(x, y, angle)

                    # calculate pixel color by tracing ray path recursively
                    color += tracePath(ray, 0)

                # average pixel value and assign
                drawingPixels[x][y] = color // len(lightSources) + NUM_SAMPLES

def tracePath(ray, depth):

    # end if ray has bounced over the limit
    if depth >= MAX_DEPTH:
        return 0

    # check if ray collisions with a light source
    for source in lightSources:
        intersection = ray.checkIntersection(Line(source.pos[0], source.pos[1], source.pos[0], source.pos[1]))
        if intersection is not None:

            # end if ray didnt bounce
            if depth == 0:
                return 0
            print ("Light source reached")
            x = int(intersection[0])
            y = int(intersection[1])
            distance = intersection[2]

            # calculate light intensity
            intensity = (1 - (distance / 500)) ** 2

            # obtain reference pixel value
            refValue = (referencePixels[y][x])[:3]

            # combine color, light source and light color
            currentValue = refValue * intensity * light

            # return pixel color
            return currentValue

    # check if ray collisions with a boundary
    for boundary in boundaries:
        intersection = ray.checkIntersection(boundary)
        if intersection is not None:

            x = int(intersection[0])
            y = int(intersection[1])
            distance = intersection[2]

            # calculate light intensity
            intensity = (1 - (distance / 500)) ** 2

            # obtain reference pixel value
            refValue = (referencePixels[y][x])[:3]

            # create a new ray
            if boundary.specular:
                # SET THE SPECULAR ANGLE BY REPLACING THE 0
                newRay = Ray(x, y, 10)
            else:
                # SET A RANDOM VALID ANGLE BY REPLACING THE 0
                newRay = randomBounce(intersection, boundary, ray)

            # obtain the incoming color
            colorIncoming = tracePath(newRay, depth + 1)

            # combine color, light source and light color
            currentValue = refValue * intensity * colorIncoming

            # return pixel color
            return currentValue

    return 0

# generate ray bouncing

# globals
WIDTH = 500
HEIGHT = 500
RUNNING = True
NUM_SAMPLES = 50
MAX_DEPTH = 2

# pygame setup
py.init()
WINDOW = py.display.set_mode([WIDTH, HEIGHT])
py.display.set_caption("2D Path Tracer")
CLOCK = py.time.Clock()

# random setup
random.seed()

# black image setup
blankImg = Image.new("RGB", (500, 500), (0, 0, 0))
drawingPixels = np.array(blankImg)

# reference image setup
refImage = Image.open("room.png")
referencePixels = np.array(refImage)

# light positions
lightSources = [LightSource(195, 200, "color"), LightSource(294, 200, "color")]

# light color
light = np.array([1, 1, 0.75])

# boundary positions
boundaries = [
            Line(180, 135, 215, 135, False),
            Line(285, 135, 320, 135, False),
            Line(320, 135, 320, 280, False),
            Line(320, 320, 320, 355, False),
            Line(320, 355, 215, 355, False),
            Line(180, 390, 180, 286, False),
            Line(180, 286, 140, 286, False),
            Line(320, 320, 360, 320, False),
            Line(180, 250, 180, 135, False),
            ]

# draw boundaries on screen
def drawBoundaries():
    for line in boundaries:
        line.draw(WINDOW)

def randomBounce (intersection, Line, ray):
    try:
        m = (Line.b[1] - Line.a[1]) / (Line.b[0] - Line.a [0])
        if m == 0:
            if ray.pos[1] > intersection [1]:
                return Ray(intersection[0], intersection[1],random.uniform(1,179))
            else:
                return Ray(intersection[0], intersection[1],random.uniform(189,359))
        else:
            b = Line.b[1] - (Line.b[0] * m)
            YL = (m * ray.pos[0]) + b
            DY = YL - ray.pos[1]
            LineAngle = np.rad2deg(np.arctan(m))
            if (m > 0) and (DY > 0):
                return Ray(intersection[0], intersection[1], random.uniform(LineAngle, LineAngle - 180))
            elif (m > 0) and (DY < 0):
                return Ray(intersection[0], intersection[1], random.uniform(LineAngle, LineAngle + 180))
            elif (m < 0) and (DY > 0):
                return Ray(intersection[0], intersection[1], random.uniform(LineAngle, LineAngle - 180))
            elif (m < 0) and (DY < 0):
                return Ray(intersection[0], intersection[1], random.uniform(LineAngle, LineAngle + 180))
    except ZeroDivisionError:
        if ray.pos[0] > intersection [0]:
            return Ray (intersection[0],intersection[1], random.choice([random.uniform(0,89),random.uniform(271,359)]))
        else:
            return Ray(intersection[0], intersection[1],random.uniform(91,269))

def specularBounce (intersection, line, ray):
    try:
        mline = (line.b[1] - line.a[1]) / (line.b[0] - line.a [0])
        LineAngle = np.rad2deg(np.arctan(mline))
        newline = Line(intersection[0], intersection[1], ray.pos[0], ray.pos[1])
        mNewLine = (newline.b[1] - newline.a[1]) / (newline.b[0] - newline.a [0])
        incidentAngle = math.atan2((mline - mNewLine), 1 + (mNewLine * mline))
        incidentAngle = np.rad2deg(incidentAngle)
        #print ("Angulo incidente: ")
        #print (incidentAngle)
        result = Ray (intersection[0],intersection[1], LineAngle + incidentAngle)
        return result
    except ZeroDivisionError:
        print ("Ray or segment are vertical")


#thread setup
tracerThread = threading.Thread(target = renderLight, daemon = True)
tracerThread.start()

# main loop
while RUNNING:

    for event in py.event.get():

        if event.type == py.QUIT:
            sys.exit()

    # set screen to white
    WINDOW.fill((255, 255, 255))

    # convert drawing image to surface and set to screen
    surface = py.surfarray.make_surface(drawingPixels)
    WINDOW.blit(surface, (0, 0))

    # update pygame
    py.display.flip()
    CLOCK.tick(60)



