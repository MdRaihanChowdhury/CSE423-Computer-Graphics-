from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import random
import math
import sys 
import time

'''
======================= variables =======================
'''
quad = gluNewQuadric()

# game
game_over = False
main_menu = True
score = 0
victory_screen = False

# window
window_height = 720
window_width = 1280

# camera 
camera_modes = ["first", "third"]
camera_index = 1   # start in third-person
fov = 90
far = 5000
near = 0.1

# space ship
ship_position = [0, 0, 0]
ship_health = 100
ship_angle = 0
ship_speed = 0.33
moving_up = False
moving_down = False
moving_left = False
moving_right = False
last_time = time.perf_counter()
cheat_mode = False
auto_target_index = 0
auto_shoot_timer = 0
auto_shoot_delay = 0.3

# projectiles
bullets = []
missiles = []
missile_count = 20
bullet_speed = 1.0
missile_speed = 0.5

# explosions
explosion_active = False
current_explosion_strength = 0.0
explosion_grow_speed = 1.0  # strength per second
max_explosion_strength = 2.0
explosions = []

# meteor
meteors = []
meteor_speed = 0.25
meteor_probability = 1
meteor_probability_upper_limit = 1000

# enemy
enemies = []
enemy_bullet = []
max_enemies = 7
current_enemy_level = 1
enemy_dist = 77 #Y-value
spawn_boss = False
enemy_colors = {
    1: (1.0, 1.0, 1.0),
    2: (1.0, 0.0, 0.0),
}
boss_position = (0, 77, 0)
boss_health = 100
boss_last_shot_time = 0
boss_shot_delay = 2.5

# powerups
powerups = []
powerup_fall_speed = 0.2

'''
======================= Drawing =======================
'''

def draw_missile_powerup(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)

    glRotatef(90, 1, 0, 0)
    glScalef(0.6, 0.6, 0.6)

    draw_missile(0, 0, 0, 0)

    glPopMatrix()

def draw_hud():
    global current_enemy_level, missile_count
    """Draw score, level, and health on the left side of the screen"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Disable depth test for HUD
    glDisable(GL_DEPTH_TEST)
    
    # Score
    glColor3f(1.0, 1.0, 0.0)  # Yellow
    glRasterPos2f(20, window_height - 40)
    score_text = f"SCORE: {score}"
    for ch in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    # Level
    glColor3f(0.0, 1.0, 1.0)  # Cyan
    glRasterPos2f(20, window_height - 70)
    level_text = f"LEVEL: {current_enemy_level}"
    for ch in level_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    # Missile
    glColor3f(0.0, 1.0, 1.0)  # Cyan
    glRasterPos2f(20, window_height - 100)
    missile_text = f"Missile Left: {missile_count}"
    for ch in missile_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    # Health bar
    glColor3f(1.0, 1.0, 1.0)  # White text
    glRasterPos2f(20, window_height - 130)
    health_text = f"HEALTH: {ship_health}"
    for ch in health_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    # Health bar visualization
    bar_width = 200
    bar_height = 20
    bar_x = 20
    bar_y = window_height - 130
    
    # Background (red)
    glColor3f(0.5, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Health fill (green/yellow/red based on health)
    health_percentage = max(0, min(100, ship_health)) / 100.0
    fill_width = bar_width * health_percentage
    
    if ship_health > 60:
        glColor3f(0.0, 1.0, 0.0)  # Green
    elif ship_health > 30:
        glColor3f(1.0, 1.0, 0.0)  # Yellow
    else:
        glColor3f(1.0, 0.0, 0.0)  # Red
    
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + fill_width, bar_y)
    glVertex2f(bar_x + fill_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Border
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    glLineWidth(1.0)
    
    # Cheat mode indicator
    if cheat_mode:
        glColor3f(1.0, 0.0, 1.0)  # Magenta
        glRasterPos2f(20, window_height - 160)
        cheat_text = "CHEAT MODE: ON"
        for ch in cheat_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    # Re-enable depth test
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
def draw_crosshair():
    global ship_position
    crosshair_size = 0.2
    x = ship_position[0]
    y = ship_position[1] + 11
    z = ship_position[2] + 1.8

    glDisable(GL_LIGHTING)
    glColor3f(1, 1, 1)  
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # Horizontal line
    glVertex3f(x - crosshair_size, y, z)
    glVertex3f(x + crosshair_size, y, z)
    # Vertical line
    glVertex3f(x, y - crosshair_size, z)
    glVertex3f(x, y + crosshair_size, z)
    glVertex3f(x, y, z - crosshair_size)
    glVertex3f(x, y, z + crosshair_size)
    glEnd()
    glLineWidth(1.0)

def draw_explosions():
    for exp in explosions:
        for p in exp["particles"]:
            life = p[6]
            if life <= 0:
                continue

            color_type = p[8]  # the stored color index

            if color_type == 0:
                glColor3f(1.0, 0.9, 0.7)   # pale yellow
            elif color_type == 1:
                glColor3f(1.0, 0.6, 0.25)  # orange
            else:
                glColor3f(0.8, 0.25, 0.1)  # dark red

            glPushMatrix()
            glTranslatef(p[0], p[1], p[2])
            size = max(0.05, p[7] * 0.1)  # scale size to something reasonable
            glScalef(size, size, size)
            glutSolidSphere(0.5, 12, 12)  # radius 0.5, 12 slices and stacks
            glPopMatrix()

def draw_spaceship():
    glPushMatrix()
   
    glTranslatef(ship_position[0], ship_position[1], ship_position[2])
    glRotatef(ship_angle, 0, 1, 0)
   
    # main body
    glPushMatrix()
    glColor3f(0.25, 0.25, 0.3)      
    glScalef(0.6, 3.5, 0.6)         
    glutSolidCube(1.0)
    glPopMatrix()
   
    # nose
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.35)
    glTranslatef(0.0, 1.9, 0.0)
    glRotatef(270, 1, 0, 0)
    gluCylinder(quad, 0.35, 0.0, 1.0, 20, 20)  
    glPopMatrix()
   
    # cockpit
    glPushMatrix()
    glColor3f(0.1, 0.3, 0.5)        
    glTranslatef(0.0, 1.0, 0.15)
    glScalef(0.8, 1.0, 1.2)
    gluSphere(quad, 0.35, 20, 20)   
    glPopMatrix()
   
    # wings
    glPushMatrix()
    glColor3f(0.22, 0.22, 0.27)
   
    # right wing
    glPushMatrix()
    glTranslatef(1.5, -0.3, 0.0)
    glRotatef(-20, 0, 1, 0)         
    glRotatef(5, 0, 0, 1)           
    glScalef(2.2, 0.15, 1.2)        
    glutSolidCube(1.0)
    glPopMatrix()
   
    # left wing
    glPushMatrix()
    glTranslatef(-1.5, -0.3, 0.0)
    glRotatef(20, 0, 1, 0)
    glRotatef(-5, 0, 0, 1)
    glScalef(2.2, 0.15, 1.2)
    glutSolidCube(1.0)
    glPopMatrix()
    glPopMatrix()
   
    # wing tips 
    glPushMatrix()
    glColor3f(0.8, 0.3, 0.1)        
   
    glPushMatrix()
    glTranslatef(2.5, -0.3, -0.3)
    glScalef(0.4, 0.2, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()
   
    glPushMatrix()
    glTranslatef(-2.5, -0.3, -0.3)
    glScalef(0.4, 0.2, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()
    glPopMatrix()
   
    # engine
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.25)
   
    # right engine
    glPushMatrix()
    glTranslatef(0.8, -1.2, 0.0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quad, 0.25, 0.28, 1.2, 20, 8)
    glPopMatrix()
   
    # left engine
    glPushMatrix()
    glTranslatef(-0.8, -1.2, 0.0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quad, 0.25, 0.28, 1.2, 20, 8)
    glPopMatrix()
    glPopMatrix()
   
    # exhaust
    glPushMatrix()
    glColor3f(0.15, 0.15, 0.18)
   
    glPushMatrix()
    glTranslatef(0.8, -2.4, 0.0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quad, 0.28, 0.22, 0.3, 20, 8)
    glPopMatrix()
   
    glPushMatrix()
    glTranslatef(-0.8, -2.4, 0.0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quad, 0.28, 0.22, 0.3, 20, 8)
    glPopMatrix()
    glPopMatrix()
   
    # glow effects
    glPushMatrix()
    glColor3f(0.2, 0.5, 1.0)
    glTranslatef(0.8, -2.5, 0.0)
    gluSphere(quad, 0.25, 16, 16)
    glTranslatef(-1.6, 0.0, 0.0)
    gluSphere(quad, 0.25, 16, 16)
    glPopMatrix()
   
    # inner glow
    glPushMatrix()
    glColor3f(0.6, 0.8, 1.0)
    glTranslatef(0.8, -2.6, 0.0)
    gluSphere(quad, 0.15, 16, 16)
    glTranslatef(-1.6, 0.0, 0.0)
    gluSphere(quad, 0.15, 16, 16)
    glPopMatrix()
   
    # side stripes
    glPushMatrix()
    glTranslatef(0.35, 0.3, 0.0)
    glScalef(0.08, 1.8, 0.62)
    glutSolidCube(1.0)
    glPopMatrix()
   
    glPushMatrix()
    glTranslatef(-0.35, 0.3, 0.0)
    glScalef(0.08, 1.8, 0.62)
    glutSolidCube(1.0)
    glPopMatrix()
   
    # Top fin
    glPushMatrix()
    glTranslatef(0.0, -1.5, -0.4)
    glRotatef(-10, 1, 0, 0)
    glScalef(0.1, 0.8, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
   
    glPopMatrix()

def draw_enemy(enemy):
    global enemy_dist
    x, y, z = enemy['position']
    glPushMatrix()
    glColor3f(*enemy['color'])
    glTranslatef(x, y, z)
    glScalef(0.22, 0.22, 0.22)
    

    glRotatef(180, 0, 0, 1)
    
    # Main body 
    glColor3f(1, 0.25, 0)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)  
    gluCylinder(gluNewQuadric(), 10, 7, 25, 16, 8)
    glPopMatrix()

    glColor3f(1, 0.25, 0)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0,0,0)
    gluSphere(gluNewQuadric(), 9,10,10)
    glPopMatrix()
    
    # Cockpit  
    glColor3f(0.2, 0.2, 0.8)  
    glPushMatrix()
    glTranslatef(0, 6, 12)
    glutSolidSphere(5, 12, 12)
    glPopMatrix()
    
    # Wings (quads) 
    glColor3f(0.7, 0.7, 0.7)  # Gray
    glBegin(GL_QUADS)
    # Right wing 
    glVertex3f(20, 15, 5)    
    glVertex3f(20, -15, 5)   
    glVertex3f(7, -15, -12)  
    glVertex3f(7, 15, -12)   
    # Left wing 
    glVertex3f(-20, 15, 5)    
    glVertex3f(-20, -15, 5)   
    glVertex3f(-7, -15, -12)  
    glVertex3f(-7, 15, -12)   
    glEnd()
    
    # Engine nacelles 
    glColor3f(0.3, 0.3, 0.3)  
    # Right engine
    glPushMatrix()
    glTranslatef(8, 0, 15) 
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 2, 8, 10, 5)
    glPopMatrix()
    # Left engine
    glPushMatrix()
    glTranslatef(-8, 0, 15)  
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 2, 8, 10, 5)
    glPopMatrix()
    
    # Engine glow  
    glColor3f(1.0, 0.5, 0.0)  
    # Right engine glow
    glPushMatrix()
    glTranslatef(8, -8, 15) 
    glutSolidSphere(2, 10, 10)
    glPopMatrix()
    # Left engine glow
    glPushMatrix()
    glTranslatef(-8, -8, 15)  
    glutSolidSphere(2, 10, 10)
    glPopMatrix()
    
    # Laser cannons 
    glColor3f(0.4, 0.4, 0.4)  # Gray
    # Right cannon
    glPushMatrix()
    glTranslatef(10, 2, -5)  
    glScalef(1.5, 1.5, 6)
    glutSolidCube(1)
    glPopMatrix()
    # Left cannon
    glPushMatrix()
    glTranslatef(-10, 2, -5)  
    glScalef(1.5, 1.5, 6)
    glutSolidCube(1)
    glPopMatrix()
    
    # Details (lines)
    glColor3f(0.9, 0.9, 0.0)  
    glBegin(GL_LINES)
    # Wing details
    glVertex3f(10, 10, 0)
    glVertex3f(10, -10, 0)
    glVertex3f(-10, 10, 0)
    glVertex3f(-10, -10, 0)
    # Body details
    glVertex3f(0, 0, 15)
    glVertex3f(0, 0, -15)
    glEnd()
    
    # Decorative points 
    glColor3f(0.0, 1.0, 0.0)  # Green
    glPointSize(3.0)
    glBegin(GL_POINTS)
    glVertex3f(12, 2, 0)
    glVertex3f(-12, 2, 0)
    glVertex3f(0, 7, 10)
    glEnd()
    
    glPopMatrix()

def draw_boss_ship():
    global boss_position

    glPushMatrix()
    glTranslatef(*boss_position)
    glRotatef(180, 0, 0, 1)  
    glScalef(2, 2, 2)

  
    # MAIN BODY 
  
    glColor3f(0.8, 0.0, 0.0)  # Dark red
    glPushMatrix()
    glScalef(3, 1.5, 6)
    glutSolidCube(2)
    glPopMatrix()

    # COCKPIT (Front sphere)
  
    glColor3f(0.0, 0.2, 0.8)  # Blue glass
    glPushMatrix()
    glTranslatef(0, 0, 7)
    glutSolidSphere(2, 20, 20)
    glPopMatrix()

    # WINGS (Flat panels)

    glColor3f(0.3, 0.3, 0.3)  # Dark gray
    # Right wing
    glPushMatrix()
    glTranslatef(8, 0, 0)
    glScalef(10, 0.2, 4)
    glutSolidCube(1)
    glPopMatrix()
    # Left wing
    glPushMatrix()
    glTranslatef(-8, 0, 0)
    glScalef(10, 0.2, 4)
    glutSolidCube(1)
    glPopMatrix()

    # ENGINES 

    glColor3f(0.2, 0.2, 0.2)
    for x in [5, -5]:
        glPushMatrix()
        glTranslatef(x, 0, -7)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 1.5, 1.2, 4, 12, 6)
        glPopMatrix()

        # Engine glow
        glColor3f(1.0, 0.5, 0.0)  # Orange
        glPushMatrix()
        glTranslatef(x, -2, -7)
        glutSolidSphere(1.2, 12, 12)
        glPopMatrix()
        glColor3f(0.2, 0.2, 0.2)  

 
    # HEAVY CANNONS (Long cuboids)
    glColor3f(0.6, 0.6, 0.6)
    # Right cannon
    glPushMatrix()
    glTranslatef(4, -1, 6)
    glScalef(0.6, 0.6, 6)
    glutSolidCube(1)
    glPopMatrix()
    # Left cannon
    glPushMatrix()
    glTranslatef(-4, -1, 6)
    glScalef(0.6, 0.6, 6)
    glutSolidCube(1)
    glPopMatrix()


    # DETAILS 
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(8, 0.5, 4)
    glVertex3f(8, 0.5, -4)
    glVertex3f(-8, 0.5, 4)
    glVertex3f(-8, 0.5, -4)
    glEnd()

    # Green navigation lights
    glColor3f(0.0, 1.0, 0.0)
    glPointSize(5.0)
    glBegin(GL_POINTS)
    glVertex3f(9, 0, 0)
    glVertex3f(-9, 0, 0)
    glEnd()

    # Red warning lights 
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_POINTS)
    glVertex3f(3, 1, 8)
    glVertex3f(-3, 1, 8)
    glEnd()

    glPopMatrix()


def draw_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)

    # main cube
    glColor3f(0.2, 0.9, 1.0)
    glScalef(0.6, 0.6, 0.6)
    glutSolidCube(1.0)

    # inner glow 
    glPushMatrix()
    glColor3f(0.6, 1.0, 1.0)
    glScalef(0.6, 0.6, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()

def draw_missile(x, y, z, angle):
    glPushMatrix()
    glTranslatef(x, y, z)

    # align with ship direction
    glRotatef(angle, 0, 0, 1)
    glRotatef(-90, 1, 0, 0)

    # body 
    glPushMatrix()
    glColor3f(0.75, 0.75, 0.75)
    gluCylinder(quad, 0.25, 0.25, 2.0, 12, 12)  
    glPopMatrix()

    # head 
    glPushMatrix()
    glColor3f(0.85, 0.2, 0.2)
    glTranslatef(0, 0, 2.0)  
    gluCylinder(quad, 0.25, 0.0, 0.8, 12, 12)  
    glPopMatrix()

    # fins 
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.3)
    glTranslatef(0.3, 0.0, 0.5)
    glScalef(0.8, 0.07, 0.45)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.3, 0.0, 0.5)
    glScalef(0.8, 0.07, 0.45)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, 0.3, 0.5)
    glScalef(0.07, 0.8, 0.45)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, -0.3, 0.5)
    glScalef(0.07, 0.8, 0.45)
    glutSolidCube(1)
    glPopMatrix()

    # flames 
    glPushMatrix()
    glColor3f(1.0, 0.6, 0.15)
    glTranslatef(0, 0, -0.3)
    gluSphere(quad, 0.18, 12, 12)
    glPopMatrix()

    glPopMatrix()

def draw_meteor(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)

    # body 
    glColor3f(0.5, 0.3, 0.2)
    glutSolidSphere(0.7, 20, 20)

    glColor3f(0.9, 0.2, 0.1)  

    # spike +X
    glPushMatrix()
    glTranslatef(0.8, 0, 0)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quad, 0.12, 0.0, 0.6, 10, 5)
    glPopMatrix()

    # spike -X
    glPushMatrix()
    glTranslatef(-0.8, 0, 0)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(quad, 0.12, 0.0, 0.6, 10, 5)
    glPopMatrix()

    # spike +Z
    glPushMatrix()
    glTranslatef(0, 0, 0.8)
    glRotatef(90, 0, 0, 1)
    gluCylinder(quad, 0.12, 0.0, 0.6, 10, 5)
    glPopMatrix()

    # spike -Z
    glPushMatrix()
    glTranslatef(0, 0, -0.8)
    glRotatef(-180, 0, 1, 0)
    gluCylinder(quad, 0.12, 0.0, 0.6, 10, 5)
    glPopMatrix()

    glPopMatrix()

def draw_enemy_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.1, 0.1)
    glutSolidSphere(0.35, 10, 10)
    glPopMatrix()

'''
======================= game function =======================
'''

def reset_value():
    pass

def update_enemies(delta_time):
    global enemies

    enemy_side_speed = 0.05  # slower side speed (adjust as needed)

    for enemy in enemies:
        # Remove forward (Y axis) movement by commenting or deleting this:
        # enemy['position'][1] -= enemy_forward_speed * 60 * delta_time

        # Initialize direction if not present: only X direction (left or right)
        if 'direction' not in enemy:
            # Randomly choose left (-1) or right (1)
            enemy['direction'] = [random.choice([-1, 1]), 0]  # [x_direction, z_direction=0]

        # Calculate new potential position on X only, no Z movement
        new_x = enemy['position'][0] + enemy['direction'][0] * enemy_side_speed * 60 * delta_time
        new_z = enemy['position'][2]  # no movement in Z

        # Check X boundaries only (between -30 and 30)
        if new_x < -30 or new_x > 30:
            # Change direction randomly when hitting boundary
            enemy['direction'][0] = random.choice([-1, 1])
            # Don't move this frame
        else:
            # Apply movement on X, keep Z same
            enemy['position'][0] = new_x
            enemy['position'][2] = new_z

    # Remove enemies out of Y bound (optional, keep if needed)
    enemies[:] = [e for e in enemies if e['position'][1] > -15]

def update_enemy_bullets(delta_time):
    speed = 0.4

    for b in enemy_bullet:
        b[1] -= speed * 60 * delta_time 

    enemy_bullet[:] = [b for b in enemy_bullet if b[1] > -50]

def enemy_shoot():
    global enemy_bullet

    current_time = time.perf_counter()

    for e in enemies:
        elapsed = current_time - e['last_shot_time']

        if elapsed >= e['next_shot_delay']:
            ex, ey, ez = e['position']

            # spawn bullet slightly in front of enemy
            enemy_bullet.append([
                ex,
                ey - 2.0,   # towards player
                ez
            ])

            # random delay
            e['last_shot_time'] = current_time
            e['next_shot_delay'] = random.uniform(3.0, 5.0)

def boss_shoot():
    global boss_last_shot_time, enemy_bullet

    current_time = time.perf_counter()
    if current_time - boss_last_shot_time < boss_shot_delay:
        return

    bx, by, bz = boss_position

    bullet_count = 10
    spread_x = 6.0
    spread_z = 4.0

    for i in range(bullet_count):
        offset_x = random.uniform(-spread_x, spread_x)
        offset_z = random.uniform(-spread_z, spread_z)

        enemy_bullet.append([
            bx + offset_x,
            by - 3.0,    
            bz + offset_z
        ])

    boss_last_shot_time = current_time
def spawn_enemy():
    global max_enemies, enemy_dist, enemy_colors, window_width, window_height
    global score
    if len(enemies) >= max_enemies:
        return
    
    level = current_enemy_level
    color = enemy_colors.get(level, (1.0, 1.0, 1.0))

    enemy = {
        'position': [random.uniform(-30, 30), enemy_dist, random.uniform(-12, 22)],
        'level': level,
        'health': current_enemy_level,
        'color': color,
        'last_shot_time': time.perf_counter(),
        'next_shot_delay': random.uniform(1.0, 5.0)
    }
    enemies.append(enemy)

def boss_entry():
    pass

def spawn_meteor():
    chance = random.randint(0, meteor_probability_upper_limit)
    if chance < meteor_probability:
        x = random.uniform(-window_width//40, window_width//40)
        y = random.uniform(80, 100)
        z = random.uniform(-5, 5)
        meteors.append([x, y, z])

def update_meteors(delta_time):
    for m in meteors:
        m[1] -= meteor_speed * 60 * delta_time

    # remove meteors that pass the ship
    meteors[:] = [m for m in meteors if m[1] > -15 ]

def create_explosion(x, y, z, strength=1.0, inherit_velocity=(0, 0, 0)):
    strength = max(0.3, strength)
    count = int(111 * strength)

    ivx, ivy, ivz = inherit_velocity
    particles = []
    
    for _ in range(count):
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)

        base_speed = random.uniform(0.2, 0.5)
        speed = base_speed * strength

        vx = math.sin(phi) * math.cos(theta) * speed + ivx
        vy = math.sin(phi) * math.sin(theta) * speed + ivy
        vz = math.cos(phi) * speed + ivz

        # Increase life proportional to strength (animation duration)
        life = random.uniform(1.0, 1.8) * strength  # multiplied by 2 to last longer
        size = random.uniform(3.0, 9.0) * strength
        color_type = random.randint(0, 2)
        particles.append([x, y, z, vx, vy, vz, life, size, color_type])

    explosions.append({
        "particles": particles,
        "delay": 0.0 * strength
    })

def update_explosions(delta_time):
    global explosions
    
    speed_factor = 50.0  # Controls particle speed; lower means slower movement
    
    for exp in explosions:
        for p in exp["particles"]:
            # Move particle based on velocity and delta time
            p[0] += p[3] * speed_factor * delta_time
            p[1] += p[4] * speed_factor * delta_time
            p[2] += p[5] * speed_factor * delta_time
            
            # Apply velocity decay (simulate inertia/friction)
            velocity_decay_rate = 0.96
            p[3] *= pow(velocity_decay_rate, delta_time * 60)
            p[4] *= pow(velocity_decay_rate, delta_time * 60)
            p[5] *= pow(velocity_decay_rate, delta_time * 60)
            
            # Decrease particle life based on delta time
            p[6] -= delta_time
            
            # Shrink particle size smoothly
            size_decay_rate = 0.985
            p[7] *= pow(size_decay_rate, delta_time * 60)
    
    # Remove explosions if all particles have no life left
    explosions = [
        exp for exp in explosions if any(p[6] > 0 for p in exp["particles"])
    ]

def update_projectiles():
    global bullets, missiles

    # bullets
    for b in bullets:
        b[1] += bullet_speed   

    # missiles
    for m in missiles:
        m[1] += missile_speed  

    bullets = [b for b in bullets if abs(b[1]) < 500]
    missiles = [m for m in missiles if abs(m[1]) < 500]

def update_powerups(delta_time):
    for p in powerups:
        p['position'][1] -= powerup_fall_speed * 60 * delta_time

    # remove if passed ship
    powerups[:] = [p for p in powerups if p['position'][1] > -15]



'''
======================= collision =======================
'''

def check_ship_powerup_collision():
    global missile_count, current_enemy_level

    ship_radius = 1.5
    powerup_radius = 1.0

    for p in powerups:
        if check_collision(ship_position, ship_radius, p['position'], powerup_radius):
            if p['type'] == 'missile':
                if current_enemy_level == 1:
                    missile_count += 1
                elif current_enemy_level == 2:
                    missile_count += 2
                print("Missile collected!")
            powerups.remove(p)
            break


def check_collision(obj1_pos, obj1_radius, obj2_pos, obj2_radius):

    dx = obj1_pos[0] - obj2_pos[0]
    dy = obj1_pos[1] - obj2_pos[1]
    dz = obj1_pos[2] - obj2_pos[2]
    
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    if distance < (obj1_radius + obj2_radius):
        return True
    return False

# Check if spaceship hits any meteor
def check_ship_meteor_collision():
    global ship_health
    ship_radius = 1.5
    meteor_radius = 0.85

    for m in meteors:
        if check_collision(ship_position, ship_radius, m, meteor_radius):
            print("Ship hit by meteor!")
            ship_health -= 25
            create_explosion(m[0], m[1], m[2], 0.44)
            meteors.remove(m)
            break

# Check if bullet hits any meteor
def check_bullet_meteor_collision():
    bullet_radius = 0.3  # approximate radius of bullet
    meteor_radius = 0.85

    global bullets
    new_bullets = []
    for b in bullets:
        hit = False
        for m in meteors:
            if check_collision(b[:3], bullet_radius, m, meteor_radius):
                print("Meteor hit by bullet!")
                meteor_vy = -meteor_speed * 60
                create_explosion(
                    m[0], m[1], m[2],
                    strength = 0.1,
                    inherit_velocity = (0, meteor_vy * 0.025, 0)
                )
                hit = True
                break
        if not hit:
            new_bullets.append(b)
    bullets = new_bullets

# check if bullet hits any enemy
def check_bullet_enemy_collision():
    global bullets, score, current_enemy_level, spawn_boss
    
    bullet_radius = .3
    enemy_radius = 3
    new_bullets = []
    for b in bullets:
        hit = False
        for e in enemies:
            if check_collision(b[:3], bullet_radius, e['position'], enemy_radius):
                print("Enemy hit by bullet!")
                ex, ey, ez = e['position']
                hit = True
                e['health'] -= 1
                if e['health'] == 0: 
                    create_explosion(ex, ey, ez, strength=1.5)
                    enemies.remove(e)
                else:
                    create_explosion(ex, ey, ez, strength=0.75)
                score += current_enemy_level
                print(score)
                if score < 10:
                    current_enemy_level = 1
                elif 10 <= score < 30:
                    current_enemy_level = 2
                else:
                    spawn_boss = True
                break
        if not hit:
            new_bullets.append(b)
    bullets = new_bullets

# check if missile hits any enemy
def check_missile_enemy_collision():
    global missiles, score, current_enemy_level
    
    bullet_radius = .6
    enemy_radius = 3

    new_missiles = []
    for m in missiles:
        hit = False
        for e in enemies:
            if check_collision(m[:3], bullet_radius, e['position'], enemy_radius):
                print("Enemy hit by bullet!")
                ex, ey, ez = e['position']
                create_explosion(ex, ey, ez, strength=1.5)
                enemies.remove(e)
                hit = True
                score += current_enemy_level
                break
        if not hit:
            new_missiles.append(m)
    missiles = new_missiles

# check if missile hits any meteor
def check_missile_meteor_collision():
    missile_radius = 0.5 
    meteor_radius = 0.7

    global missiles
    new_missiles = []
    for x in missiles:
        hit = False
        for m in meteors:
            if check_collision(x[:3], missile_radius, m, meteor_radius):
                print("Meteor hit by missile!")
                create_explosion(m[0], m[1], m[2], strength=1.5)
                meteors.remove(m)
                powerups.append({
                    "type": "missile",
                    "position": [m[0], m[1], m[2]]
                })

                hit = True
                break
        if not hit:
            new_missiles.append(x)
    missiles = new_missiles

# check if enemy bullet hits ship
def check_bullet_ship_collision():
    bullet_radius = .3
    ship_radius = 1.5

    global enemy_bullet, ship_health

    for b in enemy_bullet:
        if check_collision(ship_position, ship_radius, b, bullet_radius):
            print("Ship hit by enemy bullet!")
            ship_health -= 10
            create_explosion(b[0], b[1], b[2], 0.44)
            enemy_bullet.remove(b)
            break

def victory():
    pass

def check_bullet_boss_collision():
    global bullets, boss_position, boss_health, bullet_power

    bullet_radius = .3
    enemy_radius = 8
    new_bullets = []
    for b in bullets:
        hit = False
        if check_collision(b[:3], bullet_radius, boss_position, enemy_radius):
            print("Bullet hit the boss!")
            ex, ey, ez = boss_position
            create_explosion(ex, ey, ez, strength=1)
            boss_health -= bullet_power
            if boss_health <= 0:
                victory()
            hit = True
            break
        if not hit:
            new_bullets.append(b)
    bullets = new_bullets

# check if missile hits any enemy
def check_missile_boss_collision():
    global missiles, score, boss_health, boss_position
    
    bullet_radius = .6
    enemy_radius = 8

    new_missiles = []
    for m in missiles:
        hit = False
        if check_collision(m[:3], bullet_radius, boss_position, enemy_radius):
            print("Missile hit the boss!")
            ex, ey, ez = boss_position
            create_explosion(ex, ey, ez, strength=1.5)
            boss_health -= missile_power
            if boss_health <= 0:
                victory()
            hit = True
            break
        if not hit:
            new_missiles.append(m)
    missiles = new_missiles


'''
======================= camera =======================
'''

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, window_width / window_height, near, far)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    mode = camera_modes[camera_index]
    if mode == "first":
        setup_first_person_camera()
        draw_crosshair()
    elif mode == "third":
        setup_third_person_camera()

def setup_first_person_camera():
    global ship_position
    cam_x = ship_position[0]
    cam_y = ship_position[1] - 6
    cam_z = ship_position[2] + 3
    
    look_x = cam_x
    look_y = cam_y + 50
    look_z = cam_z
    
    gluLookAt(
        cam_x, cam_y, cam_z,
        look_x, look_y, look_z,
        0, 0, 1
    )

def setup_third_person_camera():
    cam_x = 0 
    cam_y = -15
    cam_z = 5
    
    look_x = 0
    look_y = 0
    look_z = 5
    
    gluLookAt(
        cam_x, cam_y, cam_z,
        look_x, look_y, look_z,
        0, 0, 1
    )
'''
======================= display =======================
'''

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    global window_width , window_height
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def menu_display():
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Title
    draw_text(window_width//2 - 195, window_height - 150, "SPACE ODYSSEY")

    # PLAY button
    play_x, play_y = window_width//2 - 120, window_height//2 + 40
    draw_text(play_x - 35, play_y + 70, "PLAY")
    glColor3f(0.1, 0.6, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(play_x, play_y)
    glVertex2f(play_x + 240, play_y)
    glVertex2f(play_x + 240, play_y + 60)
    glVertex2f(play_x, play_y + 60)
    glEnd()

    # QUIT button
    quit_x, quit_y = window_width//2 - 120, window_height//2 - 40
    draw_text(quit_x - 35, quit_y + 60, "QUIT")
    glColor3f(0.7, 0.1, 0.1)
    glBegin(GL_QUADS)
    glVertex2f(quit_x, quit_y)
    glVertex2f(quit_x + 240, quit_y)
    glVertex2f(quit_x + 240, quit_y + 60)
    glVertex2f(quit_x, quit_y + 60)
    glEnd()

    glutSwapBuffers()

def display():
    global game_over, main_menu, enemy_colors, enemies, spawn_boss, powerups
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  
    glViewport(0, 0, window_width, window_height)
    if not game_over and not main_menu:
        setup_camera()
        draw_spaceship()
        draw_explosions()
        for enemy in enemies:
            draw_enemy(enemy)
        if spawn_boss:
            draw_boss_ship()
        
        for p in powerups:
            if p['type'] == 'missile':
                draw_missile_powerup(
                    p['position'][0],
                    p['position'][1],
                    p['position'][2]
                )

        for b in bullets:
            draw_bullet(b[0], b[1], b[2])
        for m in missiles:
            draw_missile(m[0], m[1], m[2], m[3])
        for m in meteors:
            draw_meteor(m[0], m[1], m[2])
        for b in enemy_bullet:
            draw_enemy_bullet(b[0], b[1], b[2])
        draw_hud()
    elif main_menu == True:
        menu_display()
        return
    
    glutSwapBuffers()



'''
======================= control =======================
'''

def mouse(button, state, x, y):
    global bullets, missiles, main_menu, missile_count

    if state != GLUT_DOWN:
        return

    y = window_height - y

    if main_menu:
        # PLAY
        if (window_width//2 - 120 <= x <= window_width//2 + 120 and
            window_height//2 + 40 <= y <= window_height//2 + 100):
            main_menu = False
            game_over = False
            print("play pressed")
            return

        # QUIT
        elif (window_width//2 - 120 <= x <= window_width//2 + 120 and
            window_height//2 - 40 <= y <= window_height//2 + 20):
            print("exit pressed")
            glutLeaveMainLoop()

        return

    spawn_x = ship_position[0]         # same X as ship
    spawn_y = ship_position[1] + 1.75  # a bit in front
    spawn_z = ship_position[2]  

    if button == GLUT_LEFT_BUTTON:
        bullets.append([spawn_x, spawn_y, spawn_z, ship_angle])

    elif button == GLUT_RIGHT_BUTTON:
        if missile_count > 0:
            missile_count -= 1
            missiles.append([spawn_x, spawn_y, spawn_z, ship_angle])

def keyboard(key, x, y):
    global camera_index, ship_angle, ship_position, moving_up, moving_down, moving_left, moving_right
    global current_explosion_strength, main_menu, cheat_mode
    key = key.decode("utf-8").lower()    
    
    # Camera toggle
    if not main_menu:
        if key == "v":
            camera_index = (camera_index + 1) % 2
            print(f"Camera mode: {camera_modes[camera_index]}")
        if key == "1":
            camera_index = 0  # First person
            print(f"Camera mode: {camera_modes[camera_index]}")
        if key == "2":
            camera_index = 1  # Third person
            print(f"Camera mode: {camera_modes[camera_index]}")
        # Cheat mode toggle
        if key == "c":
            cheat_mode = not cheat_mode
            print(f"Cheat mode: {'ON' if cheat_mode else 'OFF'}")

        # Movement    
        if key == "w":
            moving_up = True
        elif key == "s":
            moving_down = True
        elif key == "a":
            moving_left = True
        elif key == "d":
            moving_right = True

        if ord(key) == 27:
            print("Exiting...")
            reset_value()
            main_menu = True


def key_up(key, x, y):
    global moving_up, moving_down, moving_left, moving_right

    key = key.decode("utf-8").lower()

    if key == "w":
        moving_up = False
    elif key == "s":
        moving_down = False
    elif key == "a":
        moving_left = False
    elif key == "d":
        moving_right = False

def auto_target_and_shoot(delta_time):
    global ship_position, bullets, auto_target_index, auto_shoot_timer
    
    if not enemies:
        return
    
    # Select target enemy based on index
    if auto_target_index >= len(enemies):
        auto_target_index = 0
    
    target = enemies[auto_target_index]
    target_x, target_y, target_z = target['position']
    
    # Move ship towards enemy position
    speed = ship_speed * 120 * delta_time  # Faster movement in cheat mode
    
    dx = target_x - ship_position[0]
    dz = target_z - ship_position[2]
    
    # Move horizontally towards target
    if abs(dx) > 0.5:
        ship_position[0] += speed if dx > 0 else -speed
    
    if abs(dz) > 0.5:
        ship_position[2] += speed if dz > 0 else -speed
    
    # Keep ship within bounds
    ship_position[0] = max(-30, min(30, ship_position[0]))
    ship_position[2] = max(-12, min(22, ship_position[2]))
    
    # Check if ship is aligned with target
    if abs(dx) < 2.0 and abs(dz) < 2.0:
        # Shoot at target
        auto_shoot_timer += delta_time
        
        if auto_shoot_timer >= auto_shoot_delay:
            spawn_x = ship_position[0]
            spawn_y = ship_position[1] + 1.75
            spawn_z = ship_position[2]
            
            bullets.append([spawn_x, spawn_y, spawn_z, ship_angle])
            auto_shoot_timer = 0
            
            # Move to next target after shooting
            auto_target_index = (auto_target_index + 1) % len(enemies)

def convert_coordinate(x,y):
    global W_Width, W_Height
    a = x - (W_Width//2)
    b = (W_Height//2) - y
    return (a,b)

'''
======================= idle func =======================
'''

def idle():
    global last_time
    global ship_position, ship_health, game_over, spawn_boss
    global moving_up, moving_down, moving_left, moving_right
    global explosion_active, current_explosion_strength, explosions
    global main_menu
    if main_menu:
        return
    current_time = time.perf_counter()
    delta_time = current_time - last_time
    last_time = current_time

    if cheat_mode:
        auto_target_and_shoot(delta_time)
    else:
        # Normal manual movement
        speed = ship_speed * 60 * delta_time  # frame-independent

        if moving_up:
            ship_position[2] += speed   # Z up
        if moving_down:
            ship_position[2] -= speed   # Z down
        if moving_left:
            ship_position[0] -= speed   # X left
        if moving_right:
            ship_position[0] += speed   # X right

        # ship boundary
        ship_position[0] = max(-30, min(30, ship_position[0]))
        ship_position[2] = max(-12, min(22, ship_position[2]))

    if ship_health <= 0: 
        game_over = True
        main_menu = 1
    if not spawn_boss:
        spawn_enemy()
    else:
        boss_entry()
        boss_shoot()

    update_powerups(delta_time)
    update_enemies(delta_time)
    update_projectiles()
    update_explosions(delta_time)
    spawn_meteor()
    update_meteors(delta_time)
    enemy_shoot()
    update_enemy_bullets(delta_time)
    check_ship_meteor_collision()
    check_ship_powerup_collision()
    check_missile_meteor_collision()
    check_missile_enemy_collision()
    check_bullet_meteor_collision()
    check_bullet_enemy_collision()
    check_bullet_ship_collision()

    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)  # Window size
    glutInitWindowPosition(60, 40)  # Window position
    glutCreateWindow(b"Space Odyssy")

    glEnable(GL_DEPTH_TEST)  #NEW
    glClearColor(0.01, 0.02, 0.04, 1) 


    glutKeyboardFunc(keyboard) 
    glutKeyboardUpFunc(key_up)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutMouseFunc(mouse)

    glutMainLoop()

if __name__ == "__main__":
    main()