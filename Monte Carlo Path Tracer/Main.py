import sys
import threading
import random
import math
from PIL import Image
from Line import *
from Light import *
from Ray import *

def renderLight():
    #while True:

        # loop through all the pixels
        for x in range (500):
            for y in range (500):

                # pixel color black
                color = 0

                # amount of rays that reached the light source
                effectiveRays = 0

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
                        currentValue = refValue * intensity * source.color

                        # add all light sources
                        color += currentValue

                # calculate indirect lighting with monte carlo
                for i in range (NUM_SAMPLES):

                    # get random direction
                    angle = random.uniform(0, 360)

                    # create ray from pixel to random direction
                    ray = Ray(x, y, angle)

                    # calculate pixel color by tracing ray path recursively
                    colorBleed = tracePath(ray, 0)

                    # take the result into account only if it is not black
                    if colorBleed.all():
                        effectiveRays += 1
                        color += colorBleed

                # average pixel value and assign
                finalColor = color // len(lightSources) + effectiveRays
                drawingPixels[x][y] = finalColor

def tracePath(ray, depth):

    # if its the last ray
    if depth >= MAX_DEPTH:

        # check if ray collisions with a light source
        for source in lightSources:
            intersection = ray.checkIntersection(Line(source.pos[0], source.pos[1] - 5, source.pos[0], source.pos[1] + 5))
            if intersection is not None:

                x = int(intersection[0])
                y = int(intersection[1])
                distance = intersection[2]

                #check if ray collision with a boundary
                collision = False
                for boundary in boundaries:
                    intersection = ray.checkIntersection(boundary)
                    if intersection is not None and intersection[2] < distance:
                        collision = True
                        break

                if not collision:

                    # calculate light intensity
                    intensity = (1 - (distance / 500)) ** 2

                    # obtain reference pixel value
                    refValue = (referencePixels[y][x])[:3]

                    # combine color, light source and light color
                    currentValue = refValue * intensity * source.color

                    # return pixel color
                    return currentValue

        # end if ray has bounced over the limit
        return BLACK

    # check if ray collisions with a boundary and find the nearest
    boundaryCollided = None
    shortestIntersection = [0, 0, 1000000]
    for boundary in boundaries:
        intersection = ray.checkIntersection(boundary)
        if intersection is not None and intersection[2] < shortestIntersection[2]:
            shortestIntersection = intersection
            boundaryCollided = boundary

    if boundaryCollided is not None:

        x = int(shortestIntersection[0])
        y = int(shortestIntersection[1])
        distance = shortestIntersection[2]

        # calculate light intensity
        intensity = (1 - (distance / 500)) ** 2

        # obtain reference pixel value
        refValue = (referencePixels[y][x])[:3]

        # create a new ray
        if boundaryCollided.specular:
            # SET THE SPECULAR ANGLE BY REPLACING THE 0
            newRay = Ray(x, y, 0)
        else:
            newRay = randomBounce(shortestIntersection, boundaryCollided, ray)

        # obtain the incoming color
        colorIncoming = tracePath(newRay, depth + 1)

        # conversion
        colorIncomingConv = [rgb / 100 for rgb in colorIncoming]

        # combine color, light source and light color
        currentValue = refValue * intensity * colorIncomingConv

        # return pixel color
        return currentValue

    return BLACK

# globals
WIDTH = 500
HEIGHT = 500
RUNNING = True
NUM_SAMPLES = 500
MAX_DEPTH = 1

# colors
YELLOW = np.array([1, 1, 0.75])
BLACK = np.array([0, 0, 0])

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
lightSources = [LightSource(195, 152, YELLOW), LightSource(305, 152, YELLOW)]

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

# draw light sources on screen
def drawLightSources():
    for source in lightSources:
        source.draw(WINDOW)

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
        LineAngle = np.rad2deg(np.arctan2((line.b[1] - line.a[1]),(line.b[0] - line.a [0])))
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

def lightDirectedBounce (intersection, line, ray):
    validSource = None
    sourcesIndexes = list(range(0,len(lightSources)))
    random.shuffle(sourcesIndexes)
    for index in sourcesIndexes:
        source = lightSources[index]
        try:
            m = (line.b[1] - line.a[1]) / (line.b[0] - line.a[0])
            if m == 0:
                if (ray.pos[1] > intersection[1] and source.pos[1] > intersection[1]) or \
                        (ray.pos[1] < intersection[1] and source.pos[1] < intersection[1]):
                    validSource = source
                    break
            else:
                raySide = 0
                sourceSide = 0
                b = line.b[1] - (line.b[0] * m)
                YL = (m * ray.pos[0]) + b
                DY = YL - ray.pos[1]
                if ((m > 0) and (DY > 0)) or ((m < 0) and (DY > 0)):
                    raySide = -1
                else:
                    raySide = 1
                YL = (m * source.pos[0]) + b
                DY = YL - source.pos[1]
                if ((m > 0) and (DY > 0)) or ((m < 0) and (DY > 0)):
                    sourceSide = -1
                else:
                    sourceSide = 1
                if sourceSide == raySide:
                    validSource = source
                    break
        except ZeroDivisionError:
            if (ray.pos[0] > intersection[0] and source.pos[0] > intersection[0]) or \
                    (ray.pos[0] < intersection[0] and source.pos[0] < intersection[0]):
                validSource = source
                break
    if validSource == None:
        return None
    rayLine = Line (intersection[0], intersection[1], source.pos[0], source.pos[1])
    LineAngle = np.rad2deg(np.arctan2((rayLine.b[1] - rayLine.a[1]), (rayLine.b[0] - rayLine.a[0])))
    return Ray (intersection[0],intersection[1], LineAngle)


# thread setup
#tracerThread = threading.Thread(target = renderLight, daemon = True)
#tracerThread.start()

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

    #drawBoundaries()
    drawLightSources()
    ray = Ray (25,170,45)
    line = Line (458,351,25,189)
    line.draw(WINDOW)
    ray.draw(WINDOW)
    bouncedRay = lightDirectedBounce(ray.checkIntersection(line), line, ray)
    if bouncedRay == None:
        print ("No valid source")
    else:
        bouncedRay.draw(WINDOW)

    # update pygame
    py.display.flip()
    CLOCK.tick(60)



