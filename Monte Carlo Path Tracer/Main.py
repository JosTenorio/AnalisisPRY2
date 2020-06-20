import sys
import threading
import random
import math
from PIL import Image
from Line import *
from Light import *
from Ray import *
import time

def renderLight():

    # loop through all the pixels
    for x in range (500):
        for y in range (500):

            # pixel color black
            color = 0
            effectiveRays = 0

            # obtain reference pixel value
            refValue = (referencePixels[y][x])[:3]

            # calculate direct lighting
            for source in lightSources:

                # create a line segment from pixel to light source
                directLine = Line(x, y, source.pos[0], source.pos[1])

                # calculate distance from pixel to light source
                sourceDist = math.sqrt(((x - source.pos[0]) ** 2)+((y - source.pos[1]) ** 2))

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
                    effectiveRays += 1
                    color += currentValue

            # calculate indirect lighting with monte carlo
            for i in range (NUM_SAMPLES):

                # get random direction
                angle = random.uniform(0, 360)

                # create ray from pixel to random direction
                ray = Ray(x, y, angle)

                # calculate pixel color by tracing ray path recursively
                pathTrace = tracePath(ray, 0)
                colorBleed = pathTrace[0]
                totalDistance = pathTrace[1]
                sourceColor = pathTrace[2]

                # if the ray reached a light source
                if colorBleed.all():

                    # add the color bleeding
                    effectiveRays += 1
                    color += colorBleed

                    # calculate light intensity
                    intensity = (1 - (totalDistance / 500)) ** 2

                    # combine color, light source and light color
                    currentValue = refValue * intensity * sourceColor

                    # add all light sources
                    effectiveRays += 1
                    color += currentValue

            # average pixel value and assign
            if effectiveRays == 0:
                finalColor = BLACK
            else:
                finalColor = color // effectiveRays
            drawingPixels[x][y] = finalColor

def tracePath(ray, depth):
    global rayG
    # if its the last ray
    if depth >= MAX_DEPTH:

        # check if ray collisions with a light source, LAST RAY SHOULD ALWAYS INTERSECT LIGHT
        for source in lightSources:
            intersection = ray.checkIntersection(Line(source.pos[0], source.pos[1] - 5, source.pos[0], source.pos[1] + 5))
            if intersection is not None:

                x = int(ray.pos[0])
                y = int(ray.pos[1])
                distance = intersection[2]

                #check if ray collisions with a boundary
                collision = False
                for boundary in boundaries:
                    intersection = ray.checkIntersection(boundary)
                    if intersection is not None and intersection[2] < distance:
                        collision = True
                        break

                if not collision:
                    #rayG = ray
                    #time.sleep(2)

                    # calculate light intensity
                    intensity = (1 - (distance / 500)) ** 2

                    # obtain reference pixel value
                    refValue = (referencePixels[y][x])[:3]

                    # combine color, light source and light color
                    currentValue = refValue * intensity * source.color

                    # return pixel color and distance
                    return [currentValue, distance, source.color]

        return [BLACK, 0, None]

    # check if ray collisions with a boundary and find the nearest
    boundaryCollided = None
    shortestIntersection = [0, 0, 1000000]
    for boundary in boundaries:
        intersection = ray.checkIntersection(boundary)
        if intersection is not None and intersection[2] < shortestIntersection[2]:
            shortestIntersection = intersection
            boundaryCollided = boundary

    if boundaryCollided is not None:

        # create a new ray
        if boundaryCollided.specular:
            # SET THE SPECULAR ANGLE BY REPLACING THE 0
            newRay = Ray(0, 0, 0)
        else:
            if depth == MAX_DEPTH - 1:
                newRay = lightDirectedBounce(shortestIntersection, boundaryCollided, ray)
            else:
                newRay = randomBounce(shortestIntersection, boundaryCollided, ray)

        if newRay is not None:
            #rayG = ray
            #time.sleep(2)

            x = int(ray.pos[0])
            y = int(ray.pos[1])
            distance = shortestIntersection[2]

            # calculate light intensity
            intensity = (1 - (distance / 500)) ** 2

            # obtain reference pixel value
            refValue = (referencePixels[y][x])[:3]

            # obtain the incoming color and distance
            pathTrace = tracePath(newRay, depth + 1)

            # conversion
            colorIncoming = [rgb / 100 for rgb in pathTrace[0]]
            totalDistance = distance + pathTrace[1]
            sourceColor = pathTrace[2]

            # combine color, light source and light color
            currentValue = refValue * intensity * colorIncoming

            # return pixel color and distance traveled
            return [currentValue, totalDistance, sourceColor]

    return [BLACK, 0, None]


# globals
WIDTH = 500
HEIGHT = 500
RUNNING = True
NUM_SAMPLES = 10
MAX_DEPTH = 1

# colors
YELLOW = np.array([1.0, 1.0, 0.75])
BLACK = np.array([0.0, 0.0, 0.0])

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

def lightDirectedBounce(intersection, boundary, ray):
    validSource = None
    sourcesIndexes = list(range(0, len(lightSources)))
    random.shuffle(sourcesIndexes)
    for index in sourcesIndexes:
        source = lightSources[index]
        try:
            m = (boundary.b[1] - boundary.a[1]) / (boundary.b[0] - boundary.a[0])
            if m == 0:
                if (ray.pos[1] > intersection[1] and source.pos[1] > intersection[1]) or (ray.pos[1] < intersection[1] and source.pos[1] < intersection[1]):
                    validSource = source
                    break
            else:
                b = boundary.b[1] - (boundary.b[0] * m)
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
            if (ray.pos[0] > intersection[0] and source.pos[0] > intersection[0]) or (ray.pos[0] < intersection[0] and source.pos[0] < intersection[0]):
                validSource = source
                break
    if validSource is not None:
        rayLine = Line(intersection[0], intersection[1], validSource.pos[0], validSource.pos[1])
        LineAngle = np.rad2deg(np.arctan2((rayLine.b[1] - rayLine.a[1]), (rayLine.b[0] - rayLine.a[0])))
        return Ray(intersection[0], intersection[1], LineAngle)
    return None

def randomBounce(intersection, boundary, ray):
    try:
        m = (boundary.b[1] - boundary.a[1]) / (boundary.b[0] - boundary.a [0])
        if m == 0:
            if ray.pos[1] > intersection [1]:
                return Ray(intersection[0], intersection[1],random.uniform(1, 179))
            else:
                return Ray(intersection[0], intersection[1],random.uniform(189, 359))
        else:
            b = boundary.b[1] - (boundary.b[0] * m)
            YL = (m * ray.pos[0]) + b
            DY = YL - ray.pos[1]
            LineAngle = np.rad2deg(np.arctan(m))
            if ((m > 0) and (DY < 0)) or ((m < 0) and (DY < 0)):
                return Ray(intersection[0], intersection[1], random.uniform(LineAngle, LineAngle + 180))
            else:
                return Ray(intersection[0], intersection[1], random.uniform(LineAngle, LineAngle - 180))
    except ZeroDivisionError:
        if ray.pos[0] > intersection[0]:
            return Ray(intersection[0], intersection[1], random.choice([random.uniform(0, 89), random.uniform(271, 359)]))
        else:
            return Ray(intersection[0], intersection[1], random.uniform(91, 269))


# colors
YELLOW = np.array([1.0, 1.0, 0.75])
BLACK = np.array([0.0, 0.0, 0.0])

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
            Line(174, 131, 215, 131, False),
            Line(285, 131, 325, 131, False),
            Line(325, 131, 325, 280, False),
            Line(325, 325, 325, 360, False),
            Line(325, 360, 215, 360, False),
            Line(174, 390, 174, 289, False),
            Line(174, 289, 142, 289, False),
            Line(325, 325, 360, 325, False),
            Line(174, 250, 174, 131, False),
            ]

# draw boundaries on screen
def drawBoundaries():
    for line in boundaries:
        line.draw(WINDOW)

# draw light sources on screen
def drawLightSources():
    for source in lightSources:
        source.draw(WINDOW)

def specularVerticalRayHorizonalSegment (intersection):
    if ray.dir[1] > 0:
        # Ray aimed downwards
        bouncedRayAngle = 270
        return Ray(intersection[0], intersection[1], bouncedRayAngle)
    else:
        # Ray aimed upwards
        bouncedRayAngle = 90
        return Ray(intersection[0], intersection[1], bouncedRayAngle)

def specularNonVerticalRayHorizonalSegment (intersection, rayLine):
    rayLineM = (rayLine.b[1] - rayLine.a[1]) / (rayLine.b[0] - rayLine.a[0])
    incidentAngle = np.rad2deg(math.atan2(1, rayLineM))
    bouncedRayAngle = np.rad2deg(np.arctan2((rayLine.b[1] - rayLine.a[1]), (rayLine.b[0] - rayLine.a[0]))) + 180 + (2 * incidentAngle)
    return Ray(intersection[0], intersection[1], bouncedRayAngle)

def specularVerticalRayNonHorizontalSegment (intersection, segmentMNumerator, segmentMDenominator):
    segmentM = segmentMNumerator / segmentMDenominator
    normalM = -1 / segmentM
    incidentAngle = np.rad2deg(math.atan2(1, normalM))
    if ray.dir[1] > 0:
        # Ray aimed downwards
        bouncedRayAngle = 270 - (2 * incidentAngle)
    else:
        # Ray aimed upwards
        bouncedRayAngle = 90 - (2 * incidentAngle)
    return Ray(intersection[0], intersection[1], bouncedRayAngle)

def specularNonVerticalRayVerticalSegment (intersection, rayLine, rayLineMDenominator):
    rayLineM = (rayLine.b[1] - rayLine.a[1]) / rayLineMDenominator
    normalM = 0
    incidentAngle = np.rad2deg(math.atan2((normalM - rayLineM), 1 + (rayLineM * normalM)))
    bouncedRayAngle = np.rad2deg(np.arctan2((rayLine.b[1] - rayLine.a[1]), (rayLine.b[0] - rayLine.a[0]))) + 180 + (2 * incidentAngle)
    return Ray(intersection[0], intersection[1], bouncedRayAngle)

def specularNonVerticalRayDiagonalSegment (intersection, segment, rayLine, segmentMDenominator, rayLineMDenominator):
    segmentM = (segment.b[1] - segment.a[1]) / segmentMDenominator
    normalM = -1 / segmentM
    rayLineM = (rayLine.b[1] - rayLine.a[1]) / rayLineMDenominator
    incidentAngle = np.rad2deg(math.atan2((normalM - rayLineM), 1 + (rayLineM * normalM)))
    bouncedRayAngle = np.rad2deg(np.arctan2((rayLine.b[1] - rayLine.a[1]), (rayLine.b[0] - rayLine.a[0]))) + 180 + (
                2 * incidentAngle)
    return Ray(intersection[0], intersection[1], bouncedRayAngle)

def specularBounce (intersection, segment, ray):
    rayLine = Line(ray.pos[0], ray.pos[1], intersection[0], intersection[1])
    segmentMNumerator = (segment.b[1] - segment.a [1])
    rayLineMDenominator = (rayLine.b[0] - rayLine.a[0])
    if segmentMNumerator == 0:
        if rayLineMDenominator == 0:
            bouncedRay = specularVerticalRayHorizonalSegment(intersection)
        else:
            bouncedRay = specularNonVerticalRayHorizonalSegment (intersection, rayLine)
    else:
        segmentMDenominator = (segment.b[0] - segment.a[0])
        if rayLineMDenominator == 0:
            bouncedRay = specularVerticalRayNonHorizontalSegment(intersection, segmentMNumerator, segmentMDenominator)
        else:
            if segmentMDenominator == 0:
                bouncedRay = specularNonVerticalRayVerticalSegment(intersection, rayLine, rayLineMDenominator)
            else:
                bouncedRay = specularNonVerticalRayDiagonalSegment(intersection, segment, rayLine, segmentMDenominator,rayLineMDenominator)
    return bouncedRay

# thread setup
# tracerThread = threading.Thread(target = renderLight, daemon = True)
# tracerThread.start()

# global ray for tests
rayG = Ray(0, 0, 270)

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

    ray = Ray (500,400,180)
    ray.draw(WINDOW)
    line = Line (400,500,400,250)
    line.draw(WINDOW)
    if ray.checkIntersection(line) is not None:
        specularBounce(ray.checkIntersection(line), line, ray).draw(WINDOW)
    # tests
    # drawBoundaries()
    # drawLightSources()
    # rayG.draw(WINDOW)

    # update pygame
    py.display.flip()
    CLOCK.tick(60)



