import turtle
t = turtle.Turtle()
t.setheading(90)
def tree(length):
    if (length > 30):
        t.forward(length)
        t.right(30)
        tree(length*0.7)
        t.left(60)
        tree(length*0.7)
        t.right(30)
        t.backward(length)

tree(100)
