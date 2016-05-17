import turtle
t = turtle.Turtle()
def drawSquare(length):
    "Draw a square with given side length"
    for i in range(4):
        t.forward(length)
        t.right(90)
