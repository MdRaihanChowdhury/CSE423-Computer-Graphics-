from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, math

# player & state
player_position = [0, 0]
player_angle = 0  
player_lie_angle = 0  
player_parts = {
    "body": [0, 0, 90],  
    "head": [0, 0, 135],  
    "arm": [20, 0, 110],  
    "leg": [10, 0, 35],   
    "gun": [0, 20, 110],  
}

# camera
camera_position = (0, 500, 500)  
first_person = False  
auto_camera = False 

# enemy & bullets
enemy_list = [{"coords": [random.randint(-500, 500), random.randint(-350, 350)]} for _ in range(5)]  # enemy list
bullets = []  
bullet_speed = 0.9  
enemy_speed = 0.01 
enemy_scale_time = 0  

# game stats
score = 0  
missed = 0  
game_end = False  
cheat_mode = False  
last_shot_time = 0  
shot_interval = 0.3  
MAX_MISSED = 5 
GRID_SIZE = 600  
FOV = 120  
MIN_DISTANCE = 150  
cheat_target_index = 0 

# enemy scale function
def get_enemy_scale():
    global enemy_scale_time
    enemy_scale_time += 0.01  # scale speed
    return 1 + 0.3 * math.sin(enemy_scale_time)  # scale value

# text function
def draw_text_screen(x, y, msg, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1)):
    glColor3f(*color) 
    glMatrixMode(GL_PROJECTION)  
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  # ortho
    glMatrixMode(GL_MODELVIEW)  
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)  # position
    for ch in msg:
        glutBitmapCharacter(font, ord(ch))  # draw char
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# hud
def render_hud():
    draw_text_screen(10, 770, f"Player Life Remaining: {MAX_MISSED - missed}")  # hud life
    draw_text_screen(10, 740, f"Game Score: {score}")  # hud score
    draw_text_screen(10, 710, f"Player Bullet Missed: {missed}")  # hud missed

# player draw
def render_player():
    global player_lie_angle
    glPushMatrix()
    glTranslatef(player_position[0], player_position[1], 0)  # translate player

    if game_end:
        glRotatef(player_lie_angle, 1, 0, 0)  # rotate lie
    else:
        glRotatef(player_angle, 0, 0, 1)  # rotate player

    # body
    glColor3f(0, 0.5, 0)  # body color
    glPushMatrix()
    glTranslatef(*player_parts["body"])
    glutSolidCube(40)  # body cube
    glPopMatrix()

    # head
    glColor3f(0, 0, 0)  # head color
    glPushMatrix()
    glTranslatef(*player_parts["head"])
    gluSphere(gluNewQuadric(), 15, 20, 20)  # head sphere
    glPopMatrix()

    # arms
    glColor3f(1, 0.8, 0.6)  # arm color
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(player_parts["arm"][0] * side, player_parts["arm"][1], player_parts["arm"][2])
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 40, 20, 20)  # arm cylinder
        glTranslatef(0, 0, 30)
        gluSphere(gluNewQuadric(), 6, 20, 20)  # arm hand
        glPopMatrix()

    # legs
    glColor3f(0, 0, 1)  # leg color
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(player_parts["leg"][0] * side, player_parts["leg"][1], player_parts["leg"][2])
        glRotatef(-90, 0, 0, 1)
        gluCylinder(gluNewQuadric(), 7, 7, 40, 20, 20)  # leg cylinder
        glPopMatrix()

    # gun
    glColor3f(0, 0, 1)  # gun color
    glPushMatrix()
    glTranslatef(*player_parts["gun"])
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 1, 30, 20, 20)  # gun cylinder
    glPopMatrix()

    glPopMatrix()

# enemy draw
def render_enemy(position):
    scale = get_enemy_scale()  # enemy scale
    glPushMatrix()
    glColor3f(1, 0, 0)  # enemy red
    glTranslatef(position[0], position[1], 90)
    glScalef(scale, scale, scale)
    gluSphere(gluNewQuadric(), 23, 20, 20)  # enemy sphere
    glPopMatrix()

    glPushMatrix()
    glTranslatef(position[0], position[1], 120)
    glColor3f(0, 0, 0)  # enemy eye
    gluSphere(gluNewQuadric(), 10, 20, 20)
    glPopMatrix()

# enemy move
def move_enemies():
    global enemy_list, player_position, game_end
    if game_end: return
    for e in enemy_list:
        dx = player_position[0] - e["coords"][0]
        dy = player_position[1] - e["coords"][1]
        dist = math.hypot(dx, dy)  # dist
        if dist > 0:
            e["coords"][0] += (dx / dist) * enemy_speed
            e["coords"][1] += (dy / dist) * enemy_speed
        if dist < 30: game_end = True  # collision

# enemy spawn
def generate_enemy_position():
    while True:
        x = random.randint(-500, 500)
        y = random.randint(-350, 350)
        dx = x - player_position[0]
        dy = y - player_position[1]
        if math.hypot(dx, dy) >= MIN_DISTANCE: return [x, y]  # min distance

# shoot bullet
def shoot_bullet(target=None):
    global bullets, player_position, player_angle, player_parts
    rad = math.radians(player_angle)
    bx = player_position[0] + math.sin(rad)
    by = player_position[1] + math.cos(rad)
    bz = player_parts["gun"][2] + 10

    if target:
        dx = target["coords"][0] - bx
        dy = target["coords"][1] - by
        dist = math.hypot(dx, dy)
        if dist != 0:
            vx = (dx / dist) * bullet_speed
            vy = (dy / dist) * bullet_speed
        else:
            vx, vy = 0, 0
    else:
        vx = -(bullet_speed * math.sin(rad))
        vy = bullet_speed * math.cos(rad)

    bullets.append({"pos": [bx, by, bz], "vel": [vx, vy]})  # add bullet

# bullet update
def update_bullets():
    global bullets, enemy_list, score, missed, game_end
    if game_end: return
    new_bullets = []
    for bullet in bullets:
        bullet["pos"][0] += bullet["vel"][0]
        bullet["pos"][1] += bullet["vel"][1]
        hit_enemy = False
        new_enemies = []
        for enemy in enemy_list:
            dx = bullet["pos"][0] - enemy["coords"][0]
            dy = bullet["pos"][1] - enemy["coords"][1]
            dist = math.hypot(dx, dy)
            if dist < 25:
                score += 1  # hit
                hit_enemy = True
                new_enemies.append({"coords": generate_enemy_position()})  # respawn
            else:
                new_enemies.append(enemy)
        enemy_list = new_enemies
        if not hit_enemy:
            if abs(bullet["pos"][0]) < GRID_SIZE and abs(bullet["pos"][1]) < GRID_SIZE:
                new_bullets.append(bullet)
            else:
                missed += 1
                if missed >= MAX_MISSED: game_end = True
    bullets = new_bullets

# bullet draw
def draw_bullets():
    for bullet in bullets:
        glPushMatrix()
        glColor3f(1, 0, 0)  # bullet color
        glTranslatef(bullet["pos"][0], bullet["pos"][1], 90)
        glutSolidCube(10)
        glPopMatrix()

# input handler
def key_handler(key, x, y):
    global player_angle, player_position, bullets, score, enemy_list, missed, game_end, cheat_mode, auto_camera, player_lie_angle
    if key == b"w":
        rad = math.radians(player_angle)
        player_position[0] += 5 * math.sin(rad)  # move forward
        player_position[1] += 5 * math.cos(rad)
    elif key == b"s":
        rad = math.radians(player_angle)
        player_position[0] -= 5 * math.sin(rad)  # move back
        player_position[1] -= 5 * math.cos(rad)
    elif key == b"a": player_angle -= 5  # rotate left
    elif key == b"d": player_angle += 5  # rotate right
    elif key == b"c": cheat_mode = not cheat_mode  # cheat toggle
    elif key == b"v": auto_camera = not auto_camera  # auto camera toggle
    elif key == b"r":  # reset
        player_position[:] = [0, 0]
        player_angle = 0
        player_lie_angle = 0
        bullets.clear()
        score, missed = 0, 0
        enemy_list[:] = [{"coords": generate_enemy_position()} for _ in range(5)]
        game_end = False

def arrow_keys(key, x, y):
    global camera_position
    cx, cy, cz = camera_position
    if key == GLUT_KEY_UP: cz += 1
    elif key == GLUT_KEY_DOWN: cz -= 1
    elif key == GLUT_KEY_LEFT: cx -= 1
    elif key == GLUT_KEY_RIGHT: cx += 1
    camera_position = (cx, cy, cz)  # camera move

def mouse_handler(button, state, x, y):
    global first_person
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN: shoot_bullet()  # shoot
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN: first_person = not first_person  # fp toggle

# camera config
def configure_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, 1.25, 0.1, 1500)  # perspective
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if first_person:
        if auto_camera and cheat_mode and enemy_list:
            nearest_enemy = min(enemy_list, key=lambda e: math.hypot(e["coords"][0]-player_position[0], e["coords"][1]-player_position[1]))
            ex, ey = nearest_enemy["coords"]
            cx = player_position[0]; cy = player_position[1]; cz = 80
            gluLookAt(cx, cy, cz, ex, ey, 90, 0, 0, 1)  # fp auto
        else:
            rad = math.radians(-player_angle)
            cx = player_position[0]+20; cy = player_position[1]+20; cz = 150
            gluLookAt(cx, cy, cz, cx+math.sin(rad), cy+math.cos(rad), cz, 0, 0, 1)  # fp manual
    else:
        x, y, z = camera_position
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)  # third person

# idle
def idle_func():
    global cheat_mode, last_shot_time, player_angle, cheat_target_index, player_lie_angle
    if cheat_mode and enemy_list and not game_end:
        target_enemy = enemy_list[cheat_target_index % len(enemy_list)]
        dx = target_enemy["coords"][0] - player_position[0]
        dy = target_enemy["coords"][1] - player_position[1]
        player_angle = math.degrees(math.atan2(dx, dy))  # rotate to enemy

        current_time = glutGet(GLUT_ELAPSED_TIME)/1000.0
        if current_time - last_shot_time > shot_interval:
            shoot_bullet(target_enemy)
            last_shot_time = current_time
            cheat_target_index += 1

    update_bullets()
    move_enemies()

    if game_end and player_lie_angle < 90: player_lie_angle += 2  # lie animation

    glutPostRedisplay()

# render scene
def render_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    configure_camera()

    # floor grid
    glBegin(GL_QUADS)
    for i in range(-GRID_SIZE, GRID_SIZE, 100):
        for j in range(-GRID_SIZE, GRID_SIZE, 100):
            if (i // 100 + j // 100) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.7, 0.5, 0.95)
            glVertex3f(i, j, 0)
            glVertex3f(i + 100, j, 0)
            glVertex3f(i + 100, j + 100, 0)
            glVertex3f(i, j + 100, 0)
    glEnd()

    # walls
    glBegin(GL_QUADS)
    glColor3f(0, 0, 1)
    glVertex3f(GRID_SIZE, GRID_SIZE, 0)
    glVertex3f(GRID_SIZE, GRID_SIZE, 100)
    glVertex3f(GRID_SIZE, -GRID_SIZE, 100)
    glVertex3f(GRID_SIZE, -GRID_SIZE, 0)

    glColor3f(0, 1, 1)
    glVertex3f(GRID_SIZE, -GRID_SIZE, 0)
    glVertex3f(GRID_SIZE, -GRID_SIZE, 100)
    glVertex3f(-GRID_SIZE, -GRID_SIZE, 100)
    glVertex3f(-GRID_SIZE, -GRID_SIZE, 0)

    glColor3f(0, 1, 0)
    glVertex3f(-GRID_SIZE, -GRID_SIZE, 0)
    glVertex3f(-GRID_SIZE, -GRID_SIZE, 100)
    glVertex3f(-GRID_SIZE, GRID_SIZE, 100)
    glVertex3f(-GRID_SIZE, GRID_SIZE, 0)

    glColor3f(1, 1, 1)
    glVertex3f(-GRID_SIZE, GRID_SIZE, 0)
    glVertex3f(-GRID_SIZE, GRID_SIZE, 100)
    glVertex3f(GRID_SIZE, GRID_SIZE, 100)
    glVertex3f(GRID_SIZE, GRID_SIZE, 0)
    glEnd()

    render_hud()
    render_player()
    draw_bullets()
    for e in enemy_list:
        render_enemy(e["coords"])

    if game_end:
        draw_text_screen(400, 400, "GAME OVER!", color=(1, 0, 0))
        draw_text_screen(380, 370, "Press 'R' to Restart", color=(1, 0, 0))

    glutSwapBuffers()

# main
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"OpenGL Shooting Game")
    glutDisplayFunc(render_scene)
    glutKeyboardFunc(key_handler)
    glutSpecialFunc(arrow_keys)
    glutMouseFunc(mouse_handler)
    glutIdleFunc(idle_func)
    glutMainLoop()

if __name__ == "__main__":
    main()
