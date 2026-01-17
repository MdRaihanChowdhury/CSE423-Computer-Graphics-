from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# Window size
W_Width, W_Height = 800, 500

# Global variables
bg_color = [1.0, 1.0, 1.0]
raindrops = []
rain_angle = 90

# Initialize raindrops
def init_raindrops(n):
    global raindrops
    raindrops = []
    for _ in range(n):
        x = random.randint(0, W_Width)  # generate random x position 
        y = random.randint(0, W_Height) # generate random y
        raindrops.append([x, y])       #raindrop append in list

# Draw wall (two triangles)
def draw_wall():
    glColor3f(0.6, 0.4, 0.2)
    glBegin(GL_TRIANGLES)
    #t1
    glVertex2f(300, 100)  # bottom-left
    glVertex2f(500, 100)  # bottom-right
    glVertex2f(500, 250)  # top-right
    #t2
    glVertex2f(300, 100) #bottom-left
    glVertex2f(500, 250) #bottom-right
    glVertex2f(300, 250) #top-right
    glEnd()

# Draw door
def draw_door():
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_TRIANGLES)
    #t1
    glVertex2f(370, 100)
    glVertex2f(430, 100)
    glVertex2f(430, 170)
    #t2
    glVertex2f(370, 100)
    glVertex2f(430, 170)
    glVertex2f(370, 170)
    glEnd()

    # door knob 
    glPointSize(6)             
    glColor3f(0.8, 0.6, 0.2)        
    glBegin(GL_POINTS)
    glVertex2f(377, 135)         #left middle   
    glEnd()

# Draw left window
def draw_left_window():
    glColor3f(0.3, 0.6, 1.0)
    glBegin(GL_TRIANGLES)
    #t1
    glVertex2f(320, 180)
    glVertex2f(360, 180)
    glVertex2f(360, 220)
    #t2
    glVertex2f(320, 180)
    glVertex2f(360, 220)
    glVertex2f(320, 220)
    glEnd()

# Draw right window
def draw_right_window():
    glColor3f(0.3, 0.6, 1.0)
    glBegin(GL_TRIANGLES)
    #t1
    glVertex2f(440, 180)
    glVertex2f(480, 180)
    glVertex2f(480, 220)
    #t2
    glVertex2f(440, 180)
    glVertex2f(480, 220)
    glVertex2f(440, 220)
    glEnd()

# Inside windows
def draw_window_cross_left():
    glColor3f(0.0, 0.0, 0.4) 
    glLineWidth(2)
    #Straight line
    glBegin(GL_LINES)
    glVertex2f(340, 180)   # bottom
    glVertex2f(340, 220)   # top

    # Horizontal line 
    glVertex2f(320, 200)   # left
    glVertex2f(360, 200)   # right
    glEnd()

def draw_window_cross_right():
    glColor3f(0.2, 0.2, 0.4)
    glLineWidth(2)

    glBegin(GL_LINES)
    # |
    glVertex2f(460, 180)
    glVertex2f(460, 220)

    # -
    glVertex2f(440, 200)
    glVertex2f(480, 200)
    glEnd()



# Draw roof
def draw_roof():
    glColor3f(1, 0, 0)
    glBegin(GL_TRIANGLES)
    glVertex2f(290, 250) 
    glVertex2f(400, 330)
    glVertex2f(510, 250)
    glEnd()

# Draw Ground
def draw_ground():
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(800, 0)
    glVertex2f(0,0)
    glVertex2f(800,200)
    glVertex2f(0, 0)
    glVertex2f(0, 200)
    glVertex2f(800, 200)

    glEnd()

def draw_backtree():
        glColor3f(0.0, 0.6, 0.0)
        for x in range(0, 801, 60):  # every 60 unit e akta triangle 
            glBegin(GL_TRIANGLES)
            glVertex2f(x + 30, 300)   # top
            glVertex2f(x, 200)        # bottom-left
            glVertex2f(x + 60, 200)   # bottom-right
            glEnd()


# Draw rain
def draw_rain():
    glLineWidth(1.5)
    glColor3f(0.2, 0.2, 0.8)
    length = 10        #raindrop length
    theta = math.radians(rain_angle) #rain agnle convert 
    dx = math.cos(theta) * length  # x offset for diagonal rain
    dy = math.sin(theta) * length  # y offset
    for d in raindrops:
        x, y = d            #current position of the drop
        glBegin(GL_LINES)
        glVertex2f(x, y)       #starting point of line
        glVertex2f(x + dx, y - dy) #endpoint of line
        glEnd()

# Update rain position
def update_rain():
    global raindrops
    theta = math.radians(rain_angle) 
    dx = math.cos(theta) * 2  #  calculate x movement per frame
    dy = math.sin(theta) * 2
    for drop in raindrops:
        drop[0] += dx  # update x position of the drop
        drop[1] -= dy  # update y position of the drop
        if drop[1] < 0 or drop[0] < 0 or drop[0] > W_Width:  #if drops move out of screen 
            drop[1] = random.randint(W_Height, W_Height)  #respown at a random above y screen
            drop[0] = random.randint(0, W_Width)          #resown at a random above x screen

# Change background color
def change_bg_color(amount):
    for i in range(3):
        bg_color[i] += amount          # add or subtract
        if bg_color[i] > 1: bg_color[i] = 1   #  max limit
        if bg_color[i] < 0: bg_color[i] = 0   #  min limit

# Draw house
def draw_house():
    draw_wall()
    draw_door()
    draw_left_window()
    draw_right_window()
    draw_roof()
    draw_window_cross_left()
    draw_window_cross_right()

def draw_ground_area():
    draw_ground()
    draw_backtree()



# Setup projection
def setup_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W_Width, 0, W_Height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# Display callback
def display():
    glClearColor(*bg_color, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    setup_projection() 
    draw_ground_area()
    draw_house()
    draw_rain()

    glutSwapBuffers()

# Animate callback
def animate():
    update_rain()
    glutPostRedisplay()

# Special keys
def special_keys(key, x, y):
    global rain_angle
    if key == GLUT_KEY_LEFT:
        rain_angle = min(rain_angle + 5, 110)
    elif key == GLUT_KEY_RIGHT:
        rain_angle = max(rain_angle - 5, 70)
    elif key == GLUT_KEY_UP:
        change_bg_color(0.01)
    elif key == GLUT_KEY_DOWN:
        change_bg_color(-0.01)

# Main function
def main_task():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(W_Width, W_Height)
    glutCreateWindow(b"Assignment 1 Task 1")
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutSpecialFunc(special_keys)
    init_raindrops(75)
    glutMainLoop()

# Run
if __name__ == "__main__":
    main_task()



############################################################################################
#########################################task-2#############################################
############################################################################################




from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time 


# Window size
W_Width, W_Height = 500, 500
points = []
ball_size = 5
speed = 0.05
freeze = False
blink = False

def draw_new_points(x, y, size):
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


# Convert GLUT mouse coordinates
def convert_coords(x, y):
    a = x - (W_Width / 2)  
    b = (W_Height / 2) - y  
    return a, b


def draw_points_with_blink(points, blink_on, size):
    for p in points:
        # set color based on blink state
        color = (0, 0, 0) if blink_on else p['color']
        glColor3f(*color)
        draw_new_points(p['x'], p['y'], size)

def is_blink_on(blink, speed=2):

    current_time = time.time()
    return blink and int(current_time * speed) % 2 == 0


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluOrtho2D(-W_Width//2, W_Width//2, -W_Height//2, W_Height//2)

    blink_on = is_blink_on(blink)  

    draw_points_with_blink(points, blink_on, ball_size)  # check blink status

    glutSwapBuffers()


def animate():
    if not freeze:
        for p in points:
            # move point
            p['x'] += p['vx'] * speed  # move horizontally
            p['y'] += p['vy'] * speed   # move vertically

            # bounce horizontally if hitting window edge
            if abs(p['x']) > W_Width // 2:
                p['vx'] *= -1

            # bounce vertically
            if abs(p['y']) > W_Height // 2:
                p['vy'] *= -1

    glutPostRedisplay()


def mouse(button, state, x, y):
    global blink
    if state != GLUT_DOWN:
        return

    if button == GLUT_RIGHT_BUTTON:  #add a new point
        px, py = convert_coords(x, y)
        points.append({
            'x': px,
            'y': py,
            'vx': random.choice([-1, 1]),  # horizontal direction
            'vy': random.choice([-1, 1]),  # vertical direction
            'color': (random.random(), random.random(), random.random()) 
        })
    elif button == GLUT_LEFT_BUTTON:
        blink = not blink

def keyboard(key, x, y):
    global freeze
    if key == b' ':
        freeze = not freeze

def special_keys(key, x, y):
    global speed
    if key == GLUT_KEY_UP:
        speed += 0.1
    elif key == GLUT_KEY_DOWN:
        speed = max(0.01, speed - 0.1)

def main_task2():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(W_Width, W_Height)
    glutCreateWindow(b"Assignment 1 Task 2: Amazing Box")
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutMouseFunc(mouse)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glClearColor(0, 0, 0, 1)
    glutMainLoop()


main_task2()

