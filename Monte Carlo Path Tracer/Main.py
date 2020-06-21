import sys
import threading
import time
from PIL import Image
from RayBounces import *

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

                # if the color was already calculated add it
                if savedColors[x][y][lightSources.index(source)].all():
                    color += savedColors[x][y][lightSources.index(source)]
                    effectiveRays += 1

                else:

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
                angle = random.uniform(0, 2 * PI)

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

        # check if ray collisions with a light source
        for source in lightSources:
            intersection = ray.checkIntersection(source)
            if intersection is not None:

                x = int(ray.pos[0])
                y = int(ray.pos[1])
                distance = intersection[2]

                # if the color for that source was already calculated return it
                if savedColors[x][y][lightSources.index(source)].all():
                    return [savedColors[x][y][lightSources.index(source)], distance, source.color]

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

                    # save the current pixels color for the selected source
                    savedColors[x][y][lightSources.index(source)] = currentValue

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
            newRay = specularBounce(shortestIntersection, boundaryCollided, ray)
        else:
            if depth == MAX_DEPTH - 1:
                newRay = lightDirectedBounce(shortestIntersection, boundaryCollided, ray, orgLightSources)
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
            colorIncoming = [rgb / 255 for rgb in pathTrace[0]]
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
NUM_SAMPLES = 50
MAX_DEPTH = 1


# colors
YELLOW = np.array([1.0, 1.0, 0.75])
ORANGE = np.array([1.0, 0.9, 0.5])
BLACK = np.array([0.0, 0.0, 0.0])
RED = np.array([1.0, 0.0, 0.0])
BLUE = np.array([0.0, 0.0, 1.0])

# definitions
PI = math.pi

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
lightSources = [
    LightSource(185, 132, YELLOW),
    LightSource(315, 132, YELLOW),
    LightSource(435, 28, ORANGE, 485, 28)
    ]
orgLightSources = organizeLightSources(lightSources)

# dynamic programing structure
savedColors = np.zeros((500, 500, len(lightSources), 3))

# boundary positions
boundaries = [
    Line(155, 100, 155, 215, False),
    Line(155, 100, 210, 100, False),
    Line(210, 100, 210, 0, False),
    Line(290, 100, 290, 0, False),
    Line(92, 286, 155, 286, False),
    Line(155, 286, 155, 425, False),
    Line(345, 100, 345, 290, False),
    Line(290, 100, 345, 100, False),
    Line(235, 380, 235, 499, False),
    Line(345, 155, 442, 155, True),
    Line(442, 155, 499, 155, False),
    Line(258, 370, 268, 360, False),
    Line(285, 343, 295, 333, False),
    Line(311, 318, 321, 308, False)
    ]

# draw boundaries on screen
def drawBoundaries():
    for line in boundaries:
        line.draw(WINDOW)

# draw light sources on screen
def drawLightSources():
    for source in lightSources:
        source.draw(WINDOW)

# thread setup
tracerThread = threading.Thread(target = renderLight, daemon = True)
tracerThread.start()

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

    # tests
    drawBoundaries()
    drawLightSources()
    # rayG.draw(WINDOW)

    # update pygame
    py.display.flip()
    CLOCK.tick(60)



