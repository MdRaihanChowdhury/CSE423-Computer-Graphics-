from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Colors
WHITE = (1.0, 1.0, 1.0)
diamond_colors = [
    (1.0, 0.0, 0.0),# Red
    (0.0, 1.0, 1.0),  
    (1.0, 0.5, 0.0),  
    (0.0, 1.0, 0.0),  
    (0.0, 0.0, 1.0),# Blue
    (1.0, 0.0, 1.0), 
    (1.0, 1.0, 0.0)   
]

# Window dimensions
window_width, window_height = 450, 600

# Player paddle configuration
catcher_width, catcher_height  = 150, 30
catcher_x = window_width / 2  # Start paddle at center
catcher_y = 30
paddle_color = WHITE

# Diamond management
queued_diamonds = []  # diamonds waiting to spawn
current_falling_diamond = None 
total_diamonds = 100

# Button positions
score_display_pos = (20, 520)
exit_button_pos = (window_width - 50, window_height - 50)
pause_button_pos = (window_width / 2, window_height - 50)
restart_button_pos = (20, 550)

# Game settings
initial_fall_speed = 200  
diamond_speed = initial_fall_speed  # Speed increases
is_paused = False
is_game_over = False
should_quit = False
player_score = 0

# Cheat mode variables
is_cheat_mode = False  
auto_move_speed = 400  # cheate mode catcher moving speed
target_x = None  # catchers targer position

frame_time = time.time()  # time between frames for smooth animation


def put_pixel(px, py, col=WHITE, size=2):
    glColor3fv(col)
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(px, py)
    glEnd()


def zone_to_zero(zone, x, y):
    if zone == 0: 
        return x, y
    elif zone == 1: 
        return y, x
    elif zone == 2: 
        return y, -x
    elif zone == 3: 
        return -x, y
    elif zone == 4: 
        return -x, -y
    elif zone == 5: 
        return -y, -x
    elif zone == 6: 
        return -y, x
    elif zone == 7: 
        return x, -y


def zero_to_zone(zone, x, y):
    if zone == 0: 
        return x, y
    elif zone == 1: 
        return y, x
    elif zone == 2: 
        return -y, x
    elif zone == 3: 
        return -x, y
    elif zone == 4: 
        return -x, -y
    elif zone == 5: 
        return -y, -x
    elif zone == 6: 
        return y, -x
    elif zone == 7: 
        return x, -y


def detect_zone(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) > abs(dy):
        if dx >= 0 and dy >= 0: 
            return 0
        elif dx >= 0 and dy <= 0: 
            return 7
        elif dx <= 0 and dy >= 0: 
            return 3
        elif dx <= 0 and dy <= 0:
            return 4
    else:
        if dx >= 0 and dy >= 0: 
            return 1
        elif dx <= 0 and dy >= 0: 
            return 2
        elif dx <= 0 and dy <= 0: 
            return 5
        elif dx >= 0 and dy <= 0:
            return 6


def draw_line_midpoint(x1, y1, x2, y2, col):
    zone = detect_zone(x1, y1, x2, y2)  #identify the zone
    x1, y1 = zone_to_zero(zone, x1, y1)  #convert to zone 0
    x2, y2 = zone_to_zero(zone, x2, y2)

    dx, dy = x2 - x1, y2 - y1
    d = 2 * dy - dx  
    E = 2 * dy
    NE = 2 * (dy - dx)

    x, y = x1, y1
    px, py = zero_to_zone(zone, x, y)  # Convert back to original zone
    put_pixel(px, py, col)

    while x < x2:
        if d <= 0:  
            d += E
            x += 1
        else:  
            d += NE
            x += 1
            y += 1
        px, py = zero_to_zone(zone, x, y)
        put_pixel(px, py, col)


# Button drawing functions
def btn_restart(x, y, col=(0.0, 1.0, 1.0)):
    draw_line_midpoint(x, y, x + 20, y - 20, col)
    draw_line_midpoint(x, y, x + 20, y + 20, col)
    draw_line_midpoint(x, y, x + 50, y, col)


def btn_pause(x, y, col=(1.0, 0.5, 0.0)):
    draw_line_midpoint(x + 10, y + 20, x + 10, y - 20, col)
    draw_line_midpoint(x - 10, y + 20, x - 10, y - 20, col)


def btn_play(x, y, col=(1.0, 0.5, 0.0)):
    draw_line_midpoint(x - 10, y + 20, x - 10, y - 20, col)
    draw_line_midpoint(x - 10, y + 20, x + 10, y, col)
    draw_line_midpoint(x - 10, y - 20, x + 10, y, col)


def btn_exit(x, y, col=(1.0, 0.0, 0.0)):
    draw_line_midpoint(x - 10, y + 10, x + 10, y - 10, col)
    draw_line_midpoint(x - 10, y - 10, x + 10, y + 10, col)


# Game objects
def draw_catcher():
    left, right = catcher_x - catcher_width / 2, catcher_x + catcher_width / 2
    inner_l, inner_r = left + 20, right - 20
    top, bottom = catcher_y, catcher_y - 20
    draw_line_midpoint(left, top, right, top, paddle_color)
    draw_line_midpoint(inner_l, bottom, inner_r, bottom, paddle_color)
    draw_line_midpoint(right, top, inner_r, bottom, paddle_color)
    draw_line_midpoint(left, top, inner_l, bottom, paddle_color)

#Draw a diamond shape centered at (cx, cy)
def draw_diamond(cx, cy, col):
    half_w = 7.5
    half_h = 15                  
     # Draw four edges of the diamond
    draw_line_midpoint(cx, cy, cx - half_w, cy + half_h, col)
    draw_line_midpoint(cx, cy, cx + half_w, cy + half_h, col)
    draw_line_midpoint(cx, cy + (2 * half_h), cx - half_w, cy + half_h, col)
    draw_line_midpoint(cx, cy + (2 * half_h), cx + half_w, cy + half_h, col)


# Game logic - AABB Collision Detection
def check_aabb_collision(diamond_x, diamond_y, catcher_x, catcher_y):
    # Diamond bounding box
    diamond_half_w = 7.5
    diamond_half_h = 15
    d_left = diamond_x - diamond_half_w
    d_right = diamond_x + diamond_half_w
    d_top = diamond_y + (2 * diamond_half_h)  # Diamond's top point
    d_bottom = diamond_y  # Diamond's bottom point
    
    # Catcher/Paddle bounding box
    c_left = catcher_x - catcher_width / 2
    c_right = catcher_x + catcher_width / 2
    c_top = catcher_y  # Catcher's top
    c_bottom = catcher_y - 20  
    
    # AABB collision check (4 conditions)
    return (d_left < c_right and      
            d_right > c_left and      
            d_bottom < c_top and     
            d_top > c_bottom)         


#Increment score and increase difficulty
def add_score():
    
    global current_falling_diamond, diamond_speed, player_score
    player_score += 1
    print("Score:", player_score)
    current_falling_diamond = None
    diamond_speed += 15  # speed increase 

#new diamond at random position
def spawn_diamond():
    
    if not is_game_over:
        x = random.randint(15, window_width - 15)  # Random horizontal position
        y = window_height - 15  # Start at top of screen
        col = random.choice(diamond_colors)  # Random color
        queued_diamonds.append((x, y, col))


#main game loop
def display():
    global diamond_speed, catcher_x, is_game_over, current_falling_diamond, paddle_color, is_paused, player_score, frame_time, target_x

    #calculate delta time for frame-independent movement
    current_time = time.time()
    delta_time = current_time - frame_time
    frame_time = current_time

    #update game statebottom
    if not is_game_over and not is_paused:
        # Spawn next diamond if none is falling
        if not current_falling_diamond and queued_diamonds:
            current_falling_diamond = queued_diamonds.pop(0)

        #auto-move paddle to catch diamond cheat mode
        if is_cheat_mode and current_falling_diamond:
            target_x, _, _ = current_falling_diamond  #get diamond's x position
            
            # move catcher towards target position
            distance = target_x - catcher_x
            if abs(distance) > 2:  # Only move if not close enough
                direction = 1 if distance > 0 else -1  # Determine left or right
                move_amount = auto_move_speed * delta_time * direction
                
                # don't overshoot the target
                if abs(move_amount) > abs(distance):
                    catcher_x = target_x
                else:
                    catcher_x += move_amount
                
                #clamp to screen boundaries
                catcher_x = max(catcher_width / 2, min(window_width - catcher_width / 2, catcher_x))

        #update falling diamond position
        if current_falling_diamond:
            dx, dy, col = current_falling_diamond
            dy -= diamond_speed * delta_time  # Move diamond down based on speed and time
            current_falling_diamond = (dx, dy, col)

            #check if diamond was caught (AABB collision detection)
            if check_aabb_collision(dx, dy, catcher_x, catcher_y):
                add_score()
            # Check if diamond hit bottom -game over-
            elif dy < 0:
                is_game_over = True
                current_falling_diamond = None
                paddle_color = (1.0, 0.0, 0.0)  # Turn catcher red
                diamond_speed = initial_fall_speed  # Reset speed
                print("Game Over! Score:", player_score)

    # Exit game if quit flag is set
    if should_quit:
        glutLeaveMainLoop()

    # Render all game elements
    glClear(GL_COLOR_BUFFER_BIT)
    draw_catcher()
    btn_restart(restart_button_pos[0], restart_button_pos[1])
    btn_pause(pause_button_pos[0], pause_button_pos[1]) if not is_paused else btn_play(pause_button_pos[0], pause_button_pos[1])
    btn_exit(exit_button_pos[0], exit_button_pos[1])

    # Draw the active falling diamond
    if current_falling_diamond:
        dx, dy, col = current_falling_diamond
        draw_diamond(dx, dy, col)

    glutSwapBuffers()  # Swap display buffers
    glutPostRedisplay()  # Request redraw


def keyboard_input(key, x, y):
    global catcher_x
    movement_step = 50  #pixels to move per keypress
    
    #only allow manual control when cheat mode is OFF
    if not is_cheat_mode:
        if key == GLUT_KEY_LEFT and not is_game_over and not is_paused:
            catcher_x = max(catcher_width / 2, catcher_x - movement_step)  # Move left, clamp to screen
        elif key == GLUT_KEY_RIGHT and not is_game_over and not is_paused:
            catcher_x = min(window_width - catcher_width / 2, catcher_x + movement_step)  # Move right, clamp to screen


def regular_keyboard_input(key, x, y):
    global is_cheat_mode, paddle_color
    
    if key == b'c' or key == b'C':
        is_cheat_mode = not is_cheat_mode
        if is_cheat_mode:
            print("Cheat Mode ACTIVATED - Auto-play enabled!")
            paddle_color = (0.0, 1.0, 0.0)  #catcher color would be green if c pressed
        else:
            print("Cheat Mode DEACTIVATED - Manual control restored")
            if not is_game_over:
                paddle_color = WHITE  # Return to white if game not over


def mouse_click(btn, state, x, y):
    global is_paused, is_game_over, should_quit
    y = window_height - y  

    if btn == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Check pause/play button
        if pause_button_pos[0] - 20 <= x <= pause_button_pos[0] + 20 and pause_button_pos[1] - 20 <= y <= pause_button_pos[1] + 20:
            is_paused = not is_paused
            print("Paused" if is_paused else "Play")
        # Check exit button
        elif exit_button_pos[0] - 10 <= x <= exit_button_pos[0] + 10 and exit_button_pos[1] - 10 <= y <= exit_button_pos[1] + 10:
            should_quit = True
            print("Game exited")
        # Check restart button
        elif restart_button_pos[0] - 25 <= x <= restart_button_pos[0] + 25 and restart_button_pos[1] - 20 <= y <= restart_button_pos[1] + 20:
            restart_game()
            print("Game Restarted")


def restart_game():
    global player_score, is_game_over, paddle_color, current_falling_diamond, is_paused, diamond_speed, is_cheat_mode, target_x
    is_paused = False
    player_score = 0
    is_game_over = False
    is_cheat_mode = False  #disable cheat mode on restart
    target_x = None
    paddle_color = WHITE  #reset paddle to white
    queued_diamonds.clear()  # Remove all queued diamonds
    current_falling_diamond = None
    diamond_speed = initial_fall_speed  # Reset to initial speed
    # Spawn fresh set of diamonds
    for idx in range(total_diamonds):
        spawn_diamond()


def init_gl():
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)


# Initialize GLUT and create window
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  #double buffering with RGB color
glutInitWindowSize(window_width, window_height)
glutCreateWindow(b"Catch the Diamonds!")

# Setup OpenGL and register callbacks
init_gl()
glutDisplayFunc(display)  #register display callback
glutSpecialFunc(keyboard_input)  #register keyboard callback for arrow keys
glutKeyboardFunc(regular_keyboard_input)  #register keyboard callback for regular keys (c key)
glutMouseFunc(mouse_click)  #register mouse callback


for x in range(total_diamonds):
    spawn_diamond()

glutMainLoop()
