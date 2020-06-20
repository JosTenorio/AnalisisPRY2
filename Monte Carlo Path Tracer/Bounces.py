from Line import *
from Light import *
from Ray import *
import random
import math

def lightDirectedBounce(intersection, boundary, ray, lightSources):
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
    mDenominator = (boundary.b[0] - boundary.a [0])
    if mDenominator != 0:
        m = (boundary.b[1] - boundary.a[1]) / mDenominator
        if m == 0:
            bouncedRay = randomHorizontalSegment(intersection, ray)
        else:
            bouncedRay = randomDiagonalSegment (intersection, boundary, ray, m)
    else:
        bouncedRay = randomVerticalSegment (intersection, ray)
    return bouncedRay


def specularBounce (intersection, segment, ray):
    rayLine = Line(ray.pos[0], ray.pos[1], intersection[0], intersection[1])
    segmentMNumerator = (segment.b[1] - segment.a [1])
    rayLineMDenominator = (rayLine.b[0] - rayLine.a[0])
    if segmentMNumerator == 0:
        if rayLineMDenominator == 0:
            bouncedRay = specularVerticalRayHorizonalSegment(intersection, ray)
        else:
            bouncedRay = specularNonVerticalRayHorizonalSegment (intersection, rayLine)
    else:
        segmentMDenominator = (segment.b[0] - segment.a[0])
        if rayLineMDenominator == 0:
            bouncedRay = specularVerticalRayNonHorizontalSegment(intersection, segmentMNumerator, segmentMDenominator, ray)
        else:
            if segmentMDenominator == 0:
                bouncedRay = specularNonVerticalRayVerticalSegment(intersection, rayLine, rayLineMDenominator)
            else:
                bouncedRay = specularNonVerticalRayDiagonalSegment(intersection, segment, rayLine, segmentMDenominator,rayLineMDenominator)
    return bouncedRay

def randomHorizontalSegment (intersection, ray):
    if ray.pos[1] > intersection[1]:
        bouncedRayAngle = random.uniform(1, 179)
    else:
        bouncedRayAngle = random.uniform(189, 359)
    return Ray(intersection[0], intersection[1],bouncedRayAngle)

def randomDiagonalSegment (intersection, boundary, ray, m):
    b = boundary.b[1] - (boundary.b[0] * m)
    YL = (m * ray.pos[0]) + b
    DY = YL - ray.pos[1]
    LineAngle = np.rad2deg(np.arctan(m))
    if ((m > 0) and (DY < 0)) or ((m < 0) and (DY < 0)):
        bouncedRayAngle = random.uniform(LineAngle, LineAngle + 180)
    else:
        bouncedRayAngle = random.uniform(LineAngle, LineAngle - 180)
    return Ray(intersection[0], intersection[1], bouncedRayAngle)

def randomVerticalSegment (intersection, ray):
    if ray.pos[0] > intersection[0]:
        bouncedRayAngle = random.choice([random.uniform(0, 89), random.uniform(271, 359)])
    else:
        bouncedRayAngle = random.uniform(91, 269)
    return Ray(intersection[0], intersection[1], bouncedRayAngle)

def specularVerticalRayHorizonalSegment (intersection, ray):
    if ray.dir[1] > 0:
        bouncedRayAngle = 270
    else:
        bouncedRayAngle = 90
    return Ray(intersection[0], intersection[1], bouncedRayAngle)

def specularNonVerticalRayHorizonalSegment (intersection, rayLine):
    rayLineM = (rayLine.b[1] - rayLine.a[1]) / (rayLine.b[0] - rayLine.a[0])
    incidentAngle = np.rad2deg(math.atan2(1, rayLineM))
    bouncedRayAngle = np.rad2deg(np.arctan2((rayLine.b[1] - rayLine.a[1]), (rayLine.b[0] - rayLine.a[0]))) + 180 + (2 * incidentAngle)
    return Ray(intersection[0], intersection[1], bouncedRayAngle)

def specularVerticalRayNonHorizontalSegment (intersection, segmentMNumerator, segmentMDenominator, ray):
    segmentM = segmentMNumerator / segmentMDenominator
    normalM = -1 / segmentM
    incidentAngle = np.rad2deg(math.atan2(1, normalM))
    if ray.dir[1] > 0:
        bouncedRayAngle = 270 - (2 * incidentAngle)
    else:
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