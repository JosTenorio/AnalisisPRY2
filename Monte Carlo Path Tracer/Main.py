import sys
import threading
import time
import timeit
from PIL import Image
from RayBounces import *

def renderLight():
    global lineG
    #time.sleep(3)
    start = timeit.default_timer()

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

                else:

                    # create a line segment from pixel to light source
                    directLine = Line(x, y, source.pos[0], source.pos[1])

                    # calculate distance from pixel to light source
                    sourceDist = math.sqrt(((x - source.pos[0]) ** 2)+((y - source.pos[1]) ** 2))

                    # check if line segments intersect
                    collision = False
                    for boundary in boundaries:
                        if not boundary.transparent:
                            intersection = directLine.checkIntersection(boundary)
                            if intersection is not None:
                                collision = True
                                break

                    if not collision:
                        #lineG = directLine
                        #time.sleep(2)

                        # calculate light intensity
                        intensity = (1 - (sourceDist / 500)) ** 2

                        # combine color, light source and light color
                        currentValue = refValue * intensity * source.color

                        # add all light sources
                        color += currentValue

            # assign direct light value
            drawingPixels[x][y] = color // len(lightSources)

            # calculate indirect lighting with monte carlo
            for i in range (NUM_SAMPLES):

                # get random direction
                angle = random.uniform(0, 2 * math.pi)

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
            if effectiveRays != 0:
                drawingPixels[x][y] = (drawingPixels[x][y] + color) // effectiveRays

    stop = timeit.default_timer()
    print('Time: ', stop - start)


def tracePath(ray, depth):
    global lineG

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
                    if not boundary.transparent:
                        shortestIntersection = ray.checkIntersection(boundary)
                        if shortestIntersection is not None and shortestIntersection[2] < distance:
                            collision = True
                            break

                if not collision:
                    #lineG = Line(ray.pos[0], ray.pos[1], intersection[0], intersection[1])
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
        if not boundary.transparent:
            intersection = ray.checkIntersection(boundary)
            if intersection is not None and intersection[2] < shortestIntersection[2]:
                shortestIntersection = intersection
                boundaryCollided = boundary

    if boundaryCollided is not None:
        #lineG = Line(ray.pos[0], ray.pos[1], shortestIntersection[0], shortestIntersection[1])
        #time.sleep(2)

        # create a new ray
        if boundaryCollided.specular:
            newRay = specularBounce(shortestIntersection, boundaryCollided, ray)
        else:
            if depth == MAX_DEPTH - 1:
                newRay = lightDirectedBounce(shortestIntersection, boundaryCollided, ray, orgLightSources)
            else:
                newRay = randomBounce(shortestIntersection, boundaryCollided, ray)

        if newRay is not None:

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
WHITE = np.array([1.0, 1.0, 1.0])

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
refImage = Image.open("Room.png")
referencePixels = np.array(refImage)

# light positions
lightSources = [
    LightSource(183, 134, YELLOW),
    LightSource(313, 134, YELLOW),
    LightSource(430, 32, ORANGE, 480, 32)
    ]
orgLightSources = organizeLightSources(lightSources)

# dynamic programing structure
savedColors = np.zeros((500, 500, len(lightSources), 3))

# boundary positions
boundaries = [
    Line(155, 101, 155, 215),
    Line(155, 102, 210, 102),
    Line(210, 103, 210, 0),
    Line(290, 103, 290, 0),
    Line(65, 288, 162, 288),
    Line(153, 287, 153, 400, False, True),
    Line(343, 101, 343, 295),
    Line(290, 102, 345, 102),
    Line(235, 380, 235, 499),
    Line(370, 128, 370, 263, True),
    Line(256, 373, 266, 363),
    Line(283, 346, 293, 336),
    Line(309, 320, 319, 310)
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
lineG = Line(0, 0, 0, 0)

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
    lineG.draw(WINDOW)

    # REFRACTION EXAMPLE
    # ray = Ray(450,250, np.deg2rad(150))
    # line1 = Line(400,100,400,500)
    # line2 = Line(300,100,300,500)
    # ray.draw (WINDOW)
    # line1.draw(WINDOW)
    # line2.draw(WINDOW)
    # refractedRay1 = refractiveBouce(ray.checkIntersection(line1), line1, ray, 1.00002926, 1.45)
    # refractedRay2 = refractiveBouce(refractedRay1.checkIntersection(line2), line2, refractedRay1, 1.45, 1.00002926)
    # refractedRay1.draw(WINDOW)
    # refractedRay2.draw(WINDOW)

    # update pygame
    py.display.flip()
    CLOCK.tick(60)



