import math
import turtle

t = turtle.Turtle()
t.shape('triangle')
t.speed(0)

def draw_window(length):
    "Draw a window of given width and height with a cross in the center"

    start_x, start_y = t.position()

    tiles_count = 2
    tile_length = length // tiles_count

    for x_step in range(tiles_count):
        for y_step in range(tiles_count):
            x = start_x + (x_step * tile_length)
            y = start_y + (y_step * tile_length)
            jump_turtle(x,y)
            draw_square(tile_length)

def jump_turtle(x,y):
    t.penup()
    t.goto(x,y)
    t.pendown()

def draw_house():
    "Draw a house consisting of a square base roof and a number of windows"

    draw_square(100)
    draw_roof(100,50)

    start_x = 20
    start_y = -25
    for x_step in range(2):
        for y_step in range(2):
            x = start_x + x_step * 60
            y = start_y - y_step * 60
            jump_turtle(x,y)
            draw_window(16)

def draw_roof(width,height):
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

def draw_square(length):
    "Draw a square with given side length"

    for i in range(4):
        t.forward(length)
        t.right(90)

draw_house()
