import math
import turtle
t = turtle.Turtle()
def drawSquare(length):
    """Draw a square with given side length"""
    print 'Draw a square'
def drawRoof(width, height):
    """Draw a triangular roof with given width and height"""
    print 'Draw a roof'
def drawWindow(width, height):
    """Draw a window of given width and height with a cross in the center"""
    print 'Draw a window'
def drawHouse():
    """Draw a house consisting of a square base roof and a number of windows"""
    drawSquare(100)
    drawRoof(100, 50)
    drawWindow(12, 16)
drawHouse()
