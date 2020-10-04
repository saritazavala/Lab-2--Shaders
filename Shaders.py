#Universidad del Valle de Guatemala
#Sara Zavala 18893
#Laboratorio 2 - Shaders
#Graficas

# ------------------------------------------------------------

import struct
import math
from Obj import Obj
from collections import namedtuple

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])


# -----------------------------------------------------------------------

def char(c):
    return struct.pack('=c', c.encode('ascii'))


# 2 bytes
def word(c):
    return struct.pack('=h', c)


# 4 bytes
def dword(c):
    return struct.pack('=l', c)


def color(red, green, blue):
    return bytes([round(blue * 255), round(green * 255), round(red * 255)])


def color2(r, g, b):
    return bytes([b, g, r])


# Funciones matematicas dadas por Denis en clase ----------------------------

def sum(v0, v1):
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)


def sub(v0, v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)


def mul(v0, k):
    return V3(v0.x * k, v0.y * k, v0.z * k)


def dot(v0, v1):
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z


def cross(v1, v2):
    return V3(
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x,
    )


def length(v0):
    return (v0.x ** 2 + v0.y ** 2 + v0.z ** 2) ** 0.5


def norm(v0):
    v0length = length(v0)

    if not v0length:
        return V3(0, 0, 0)

    return V3(v0.x / v0length, v0.y / v0length, v0.z / v0length)


def bbox(*vertices):
    xs = [vertex.x for vertex in vertices]
    ys = [vertex.y for vertex in vertices]

    return (max(xs), max(ys), min(xs), min(ys))


def barycentric(A, B, C, P):
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x),
        V3(B.y - A.y, C.y - A.y, A.y - P.y)
    )

    if abs(cz) < 1:
        return -1, -1, -1

    u = cx / cz
    v = cy / cz
    w = 1 - (cx + cy) / cz

    return w, v, u


# -------------------------------------------------------------------------


class Render(object):

    # Initial values -------------------------------

    def __init__(self, filename):
        self.width = 0
        self.height = 0
        self.framebuffer = []
        self.change_color = color(0, 0, 0)
        self.filename = filename
        self.x_position = 0
        self.y_position = 0
        self.ViewPort_height = 0
        self.ViewPort_width = 0
        self.glClear()

    # File Header ----------------------------------

    def header(self):
        doc = open(self.filename, 'bw')
        doc.write(char('B'))
        doc.write(char('M'))
        doc.write(dword(54 + self.width * self.height * 3))
        doc.write(dword(0))
        doc.write(dword(54))
        self.info(doc)

    # Info header ---------------------------------------

    def info(self, doc):
        doc.write(dword(40))
        doc.write(dword(self.width))
        doc.write(dword(self.height))
        doc.write(word(1))
        doc.write(word(24))
        doc.write(dword(0))
        doc.write(dword(self.width * self.height * 3))
        doc.write(dword(0))
        doc.write(dword(0))
        doc.write(dword(0))
        doc.write(dword(0))

        # Image ----------------------------------
        for x in range(self.height):
            for y in range(self.width):
                doc.write(self.framebuffer[x][y])
        doc.close()

    # Cleans a full image with the color defined in "change_color"
    def glClear(self):
        self.framebuffer = [[self.change_color for x in range(self.width)] for y in range(self.height)]
        self.zbuffer = [[-float('inf') for x in range(self.width)] for y in range(self.height)]

    # Writes all the doc
    def glFinish(self):
        self.header()

    # Draws a point according ot frameBuffer
    def glpoint(self, x, y):
        self.framebuffer[y][x] = self.change_color

    # Creates a window
    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height

    # MODELS --------------------------------------
    def triangle(self, A, B, C):
        xmax, ymax, xmin, ymin = bbox(A, B, C)

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:
                    continue
                z = A.z * w + B.z * u + C.z * v
                try:
                    if z > self.zbuffer[x][y]:
                        self.glpoint(x, y)
                        self.zbuffer[x][y] = z
                except:
                    pass

    # New function for loading my .obj
    def load_model(self, filename, translate=(0, 0, 0), scale=(1, 1, 1)):
        model = Obj(filename)

        light = V3(0, 0, 1)

        for face in model.faces:
            vcount = len(face)

            if vcount == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = V3(model.vertex[f1][0], model.vertex[f1][1], model.vertex[f1][2])
                v2 = V3(model.vertex[f2][0], model.vertex[f2][1], model.vertex[f2][2])
                v3 = V3(model.vertex[f3][0], model.vertex[f3][1], model.vertex[f3][2])

                x1 = round((v1.x * scale[0]) + translate[0])
                y1 = round((v1.y * scale[1]) + translate[1])
                z1 = round((v1.z * scale[2]) + translate[2])

                x2 = round((v2.x * scale[0]) + translate[0])
                y2 = round((v2.y * scale[1]) + translate[1])
                z2 = round((v2.z * scale[2]) + translate[2])

                x3 = round((v3.x * scale[0]) + translate[0])
                y3 = round((v3.y * scale[1]) + translate[1])
                z3 = round((v3.z * scale[2]) + translate[2])

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)

                normal = norm(cross(sub(B, A), sub(C, A)))
                intensity = dot(normal, light)
                grey = round(255 * intensity)

                if grey < 0:
                    continue

                self.change_color = color2(grey, grey, grey)

                self.triangle(A, B, C)

            else:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                v1 = V3(model.vertex[f1][0], model.vertex[f1][1], model.vertex[f1][2])
                v2 = V3(model.vertex[f2][0], model.vertex[f2][1], model.vertex[f2][2])
                v3 = V3(model.vertex[f3][0], model.vertex[f3][1], model.vertex[f3][2])
                v4 = V3(model.vertex[f4][0], model.vertex[f4][1], model.vertex[f4][2])

                x1 = round((v1.x * scale[0]) + translate[0])
                y1 = round((v1.y * scale[1]) + translate[1])
                z1 = round((v1.z * scale[2]) + translate[2])

                x2 = round((v2.x * scale[0]) + translate[0])
                y2 = round((v2.y * scale[1]) + translate[1])
                z2 = round((v2.z * scale[2]) + translate[2])

                x3 = round((v3.x * scale[0]) + translate[0])
                y3 = round((v3.y * scale[1]) + translate[1])
                z3 = round((v3.z * scale[2]) + translate[2])

                x4 = round((v4.x * scale[0]) + translate[0])
                y4 = round((v4.y * scale[1]) + translate[1])
                z4 = round((v4.z * scale[2]) + translate[2])

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)
                D = V3(x4, y4, z4)

                normal = norm(cross(sub(B, A), sub(C, A)))
                intensity = dot(normal, light)
                grey = round(255 * intensity)
                if grey < 0:
                    continue

                self.change_color = color2(grey, grey, grey)

                self.triangle(A, B, C)

                self.triangle(A, D, C)

    #Takes a new color  
    def glClearColor(self, red,blue,green):
        self.change_color = color(red,blue,green)
        #Defines the area where will be able to draw
    def glViewPort(self, x_position, y_position,  ViewPort_width, ViewPort_height):
        self.x_position = x_position
        self.y_position = y_position
        self.ViewPort_height = ViewPort_height
        self.ViewPort_width = ViewPort_width

    #Compuse el vertex por que me daba error el range
    def glVertex(self, x, y):
        x_temp  = round((x + 1) * (self.ViewPort_width/ 2) + self.x_position)
        y_temp  = round((y + 1) * (self.ViewPort_height/2) + self.y_position)
        self.glpoint(round(x_temp ), round(y_temp ))
        #Codigo basado en codigo visto en clase
    #Dennis Aldana 2020
    def glLine(self, x1, y1, x2, y2):

        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        steep = dy > dx

        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            dy = abs(y2 - y1)
            dx = abs(x2 - x1)

        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        offset = 0
        threshold = 1
        y = y1
        for x in range(x1, x2):
            if steep:
                self.glpoint(y, x)
            else:
                self.glpoint(x, y)

            offset += dy * 2

            if offset >= threshold:
                y += 1 if y1 < y2 else -1
                threshold += 2 * dx

    def shader(self, x, y, z):
        # Colores a utilizar
        c1 = [20, 36, 169]
        c2 = [62, 84, 232]
        c3 = [62, 102, 249]
        c4 = [96, 129, 255]
        c5 = [137, 243, 255]

        # Gradiente de la derecha y parte superior
        if x > 305 and y > 280:
            dx = x - 335
            dy = y - 280
            dst = math.sqrt(dx ** 2 + dy ** 2)

            if dst >= 190:
                r = (250 - dst) / 60
                return color(int(c2[0] * r), int(c2[1] * r), int(c2[2] * r))
            else:
                if y > 170:
                    dx = 335 - x
                    dy = y - 170
                    dst = math.sqrt(dx ** 2 + dy ** 2)
                    if dst >= 230:
                        r = (250 - dst) / 20
                        r1 = int(c2[1] + 18 * r)
                        r2 = int(c2[2] + 17 * r)
                        return color(c3[0], r1, r2)
                    else:
                        # Remolino en el centro
                        if y > 320:
                            dx = 400 - x
                            dy = y - 50
                            dst = math.sqrt(dx ** 2 + dy ** 2)
                            if dst <= 285:
                                return color(c1[0], c1[1], c1[2])
                            elif dst <= 295:
                                return color(c2[0], c2[1], c2[2])
                            elif dst <= 297 and x < 400 and x > 370:
                                return color(c5[0], c5[1], c5[2])
                            else:
                                return color(c3[0], c3[1], c3[2])
                        else:
                            dx = 400 - x
                            dy = y - 550
                            dst = math.sqrt(dx ** 2 + dy ** 2)
                            if dst <= 245:
                                return color(c1[0], c1[1], c1[2])
                            elif dst <= 248:
                                if x < 380 and x > 350:
                                    return color(c5[0], c5[1], c5[2])
                                else:
                                    return color(c2[0], c2[1], c2[2])
                            elif dst <= 260:
                                return color(c2[0], c2[1], c2[2])
                            elif dst <= 265:
                                if x < 400 and x > 330:
                                    return color(c5[0], c5[1], c5[2])
                                else:
                                    return color(c2[0], c2[1], c2[2])
                            else:
                                return color(c3[0], c3[1], c3[2])
                else:
                    return color(c3[0], c3[1], c3[2])

        else:
            # Gradiente de la parte izquierda
            if x > 270 and x < 295 and y > 230 and y < 260:
                dx = x - 270
                if y > 230:
                    dy = y - 230
                else:
                    dy = 260 - y
                dst = dx + dy
                if dst < 20:
                    # Triangulo de la izquierda inferior
                    return color(c4[0], c4[1], c4[2])
                else:
                    return color(c3[0], c3[1], c3[2])
            else:
                if y > 300:
                    dx = 335 - x
                    dy = y - 300
                    dst = math.sqrt(dx ** 2 + dy ** 2)
                    if dst > 100:

                        r = (120 - dst) / 20
                        r1 = int(c2[1] + 18 * r)
                        r2 = int(c2[2] + 17 * r)
                        return color(c3[0], r1, r2)
                    else:
                        return color(c3[0], c3[1], c3[2])
                else:
                    if y > 100:
                        dx = x - 400
                        dy = y
                        dst = math.sqrt(dx ** 2 + dy ** 2)

                        # Circulos de la parte inferior con gradiente
                        if dst >= 240:
                            if x > 503:
                                dx = x - 335
                                dy = y - 280
                                dst = math.sqrt(dx ** 2 + dy ** 2)

                                if dst >= 190:
                                    r = (250 - dst) / 60
                                    return color(int(c2[0] * r), int(c2[1] * r), int(c2[2] * r))
                                else:
                                    return color(c3[0], c3[1], c3[2])
                            else:
                                if dst <= 155:
                                    r = (155 - dst) / 5
                                    r1 = int(c3[1] - 18 * r)
                                    r2 = int(c3[2] - 17 * r)
                                    return color(c3[0], r1, r2)
                                else:
                                    return color(c3[0], c3[1], c3[2])
                        elif dst >= 180:
                            r = (250 - dst) / 70
                            r1 = int(c2[1] + 18 * r)
                            r2 = int(c2[2] + 17 * r)
                            return color(c3[0], r1, r2)

                        else:
                            r = (dst) / 180
                            return color(int(c3[0] * r), int(c3[1] * r), int(c3[2] * r))

                    else:
                        return color(c3[0], c3[1], c3[2])


r = Render('Lab2.bmp')
r.glCreateWindow(800, 600)
r.glClear()
r.load_model('./sphere.obj', translate=[1.13, 0.84, 1], scale=[350, 350, 350])
r.glFinish()




