from Point import *
import math

def raySegmentIntersect(ori, dir, p1, p2):

    #calculate vectors
    v1 = ori - p1
    v2 = p2 - p1
    v3 = Point(-dir.y, dir.x)

    
    dot = v2.dot(v3)
    if (abs(dot) < 0.000001):
        return -1.0

    t1 = v2.cross(v1) / dot
    t2 = v1.dot(v3) / dot

    if (t1 >= 0.0 and (t2 >= 0.0 and t2 <= 1.0)):
        return t1

    return -1.0

def length(v1):
    #assumes v1 starts at (0,0)
    return math.sqrt(v1.x*v1.x + v1.y*v1.y)


def normalize(v1):
    #assumes v1 starts at (0,0)
    v1 = v1 / length(v1)
    return v1

def intersectionPoint(ori, dir, dist):
    x = ori.x + dir.x*dist
    y = ori.y + dir.y*dist

    return Point(x,y)

def cosAngle(a, b, ori):
    #returns the cosine of the angle of 2 vectors that part from ori

    v1 = ori - a
    v2 = ori - b

    cos = v1.dot(v2)/(length(v1)*length(v2))
    return cos
