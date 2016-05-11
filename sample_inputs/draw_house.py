import math
import turtle

t = turtle.Turtle()

def drawHouse():
    "Draw a house consisting of a square base roof and a number of windows"
    drawSquare(100)
    drawRoof(100,50)

    x,y = 25,-10
    for i in range(2):
        for j in range(2):
            t.penup()
            t.goto(x+i*60,y-j*60)
            t.pendown()
            drawWindow(12,16)

def drawSquare(length):
    "Draw a square with given side length"
    for i in range(4):
        t.forward(length)
        t.right(90)

def drawRoof(width,height):
    "Draw a triangular roof with given width and height"
    t.forward(width)
    radians = math.atan(height/(width/2))
    degrees = math.degrees(radians)
    t.left(180 - degrees)
    diagonal = math.sqrt((width/2)**2+height**2)
    t.forward(diagonal)
    t.left(180 - 2*degrees)
    t.forward(diagonal)
    t.right(degrees)

def drawWindow(width,height):
    "Draw a window of given width and height with a cross in the center"
    t.forward(width/2)
    t.left(90)
    t.forward(height)
    t.backward(height)
    t.right(90)
    t.forward(width/2)
    t.left(90)
    t.forward(height/2)
    t.left(90)
    t.forward(width)
    t.backward(width)
    t.right(90)
    t.forward(height/2)
    t.left(90)
    t.forward(width)
    t.left(90)
    t.forward(height)
    t.left(90)

if (__name__ == "__main__"):
    drawHouse()
    input()
