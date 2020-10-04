#Universidad del Valle de Guatemala
#Sara Zavala 18893
#Laboratorio 2 - Shaders
#Graficas

import struct
from Obj import Obj

# -------------------------------------------------------
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
# ------------------------------------------------------------

def Render(object):

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
    # ---------------------------------------------

    #File Header ----------------------------------

    def header(self):
        doc = open(self.filename,'bw')
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



