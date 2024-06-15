import pygame
import pygame_gui
import sys
import math

# Initialize Pygame
pygame.init()

# Set up the screen
game_screen_width = 800
game_screen_height = 600
screen = pygame.display.set_mode((1100, game_screen_height), pygame.SRCALPHA)
pygame.display.set_caption("Dot in the Middle")

# Set up GUI manager
manager = pygame_gui.UIManager((1100, game_screen_height))

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
TRANSPARENT_GREEN = (0, 255, 0, 128)
TRANSPARENT_RED = (255, 0, 0, 128)
LIGHT_GRAY = (200, 200, 200)

# Dot parameters
dot_radius = 10
dot_color = RED
dot_mass = 1  # Mass of the dot

# Sliders for angle, force, and mass
angle_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect(900, 100, 140, 32),
                                                      start_value=45, value_range=(0, 100), manager=manager)
force_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect(900, 150, 140, 32),
                                                      start_value=500, value_range=(0, 5000), manager=manager)
mass_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect(900, 200, 140, 32),
                                                     start_value=1, value_range=(0.1, 10), manager=manager)

# Labels for sliders
angle_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(900, 80, 140, 20),
                                          text='Angle: 45', manager=manager)
force_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(900, 130, 140, 20),
                                          text='Force: 500', manager=manager)
mass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(900, 180, 140, 20),
                                         text='Mass: 1', manager=manager)

# Launch button
button_rect = pygame.Rect(900, 250, 140, 40)
launch_button = pygame_gui.elements.UIButton(relative_rect=button_rect, text='Launch', manager=manager)

# Rectangle definitions for interactive areas
angle_rect = pygame.Rect(900, 80, 140, 20)  # Adjust dimensions as needed
force_rect = pygame.Rect(900, 130, 140, 20)  # Adjust dimensions as needed
mass_rect = pygame.Rect(900, 180, 140, 20)   # Adjust dimensions as needed

# Initial velocity vector
v = [0, 0]
g = 981  # Adjusted gravitational acceleration for better control

# Font setup for text display
font = pygame.font.Font(None, 36)

class Block:
    """ Represents a block with friction and bounciness properties. """
    def __init__(self, f=1, b=0.8):
        self.friction = f
        self.bounciness = b

class Spawn:
    """ Represents a spawn point for the dot. """
    pass

class Goal:
    """ Represents an end goal point for the dot. """
    pass

class Death:
    """ Represents a death point for the dot. """
    pass

# Grid setup with varying block properties and special points
map = [
    [Block(), None, Block(), None, Block(), None, Block()],
    [Block(), None, None, None, None, None, Block()],
    [Block(), None, Block(), None, Block(), None, Block()],
    [Block(), Spawn(), Block(), None, Block(), None, Block()],
    [Block(), Block(), Block(), Death(), Block(), Goal(), Block()],
]

# Determine spawn position
block_width = game_screen_width // len(map[0])
block_height = game_screen_height // len(map)
spawn_x = spawn_y = 0

for row_index, row in enumerate(map):
    for col_index, item in enumerate(row):
        if isinstance(item, Spawn):
            spawn_x = col_index * block_width + block_width // 2
            spawn_y = row_index * block_height + block_height // 2

# Set the initial position of the dot
dot_position = [spawn_x, spawn_y]

goal_reached = False
death_reached = False  # New state for death
ball_launched = False  # New state for ball launch

# List to store the dot's path
dot_path = []

# Calculate initial velocity
def calculate_velocity(angle, force, mass):
    radians = math.radians(angle)
    return [-force * math.cos(radians) / mass, -force * math.sin(radians) / mass]

def check_collision(dot_pos, prev_dot_pos, block_map, v):
    global goal_reached, death_reached
    block_width = game_screen_width // len(block_map[0])
    block_height = game_screen_height // len(block_map)
    column = int(dot_pos[0] / block_width)
    row = int(dot_pos[1] / block_height)

    if 0 <= column < len(block_map[0]) and 0 <= row < len(block_map):
        # Check all four edges of the ball
        edges = [
            (dot_pos[0] - dot_radius, dot_pos[1]),  # Left edge
            (dot_pos[0] + dot_radius, dot_pos[1]),  # Right edge
            (dot_pos[0], dot_pos[1] - dot_radius),  # Top edge
            (dot_pos[0], dot_pos[1] + dot_radius)  # Bottom edge
        ]

        for edge in edges:
            edge_column = int(edge[0] / block_width)
            edge_row = int(edge[1] / block_height)

            if 0 <= edge_column < len(block_map[0]) and 0 <= edge_row < len(block_map):
                block = block_map[edge_row][edge_column]
                if isinstance(block, Block):
                    handle_block_collision(edge_column, edge_row, block, dot_pos, prev_dot_pos, v)
                elif isinstance(block, Goal):
                    goal_reached = True
                elif isinstance(block, Death):
                    death_reached = True

def handle_block_collision(column, row, block, dot_pos, prev_dot_pos, v):
    block_x = column * block_width
    block_y = row * block_height

    dx = dot_pos[0] - (block_x + block_width / 2)
    dy = dot_pos[1] - (block_y + block_height / 2)
    abs_dx = abs(dx)
    abs_dy = abs(dy)

    prev_dx = prev_dot_pos[0] - (block_x + block_width / 2)
    prev_dy = prev_dot_pos[1] - (block_y + block_height / 2)
    prev_abs_dx = abs(prev_dx)
    prev_abs_dy = abs(prev_dy)

    if prev_abs_dx > prev_abs_dy:  # Ball was primarily moving horizontally
        if prev_dx > 0:  # Ball was moving from the left to the right
            dot_pos[0] = block_x + block_width + dot_radius
        else:  # Ball was moving from the right to the left
            dot_pos[0] = block_x - dot_radius
        v[0] = -v[0] * block.bounciness if block.bounciness > 0 else 0

    else:  # Ball was primarily moving vertically
        if prev_dy > 0:  # Ball was moving from the top to the bottom
            dot_pos[1] = block_y + block_height + dot_radius
        else:  # Ball was moving from the bottom to the top
            dot_pos[1] = block_y - dot_radius

        g = 9.81  # gravity acceleration
        block_bottom = block_y + block_height if prev_dy > 0 else block_y

        value_inside_sqrt = (v[1] ** 2) - (2 * (dot_pos[1] + dot_radius - block_bottom) * g)
        if value_inside_sqrt < 0:
            v[1] = 0  # Avoid math domain error
        else:
            v[1] = -1 * block.bounciness * math.sqrt(value_inside_sqrt)
        if 0 > v[1] > -5:
            v[1] = 0

def reset_game():
    global dot_position, v, goal_reached, death_reached, ball_launched, dot_path
    dot_position = [spawn_x, spawn_y]
    v = [0, 0]
    goal_reached = False
    death_reached = False
    ball_launched = False
    dot_path = []

# Main game loop
running = True
start_pos = (0, 0)
p_time = pygame.time.get_ticks()

# Clock to manage frame rate
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60) / 1000.0  # Keep the game running at 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle pygame_gui events
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == launch_button:
                    angle = angle_slider.get_current_value()
                    force = force_slider.get_current_value()
                    mass = mass_slider.get_current_value()
                    dot_mass = mass
                    v = calculate_velocity(angle, force, dot_mass)
                    ball_launched = True
                    dot_path = []
                    dot_position = [spawn_x, spawn_y]
                    goal_reached = False
                    death_reached = False

        # Process other pygame_gui events
        manager.process_events(event)

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == angle_slider:
                angle_label.set_text(f'Angle: {int(angle_slider.get_current_value())}')
            elif event.ui_element == force_slider:
                force_label.set_text(f'Force: {int(force_slider.get_current_value())}')
            elif event.ui_element == mass_slider:
                mass_label.set_text(f'Mass: {mass_slider.get_current_value():.1f}')

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if angle_rect.collidepoint(event.pos):
                input_active = 'angle'
            elif force_rect.collidepoint(event.pos):
                input_active = 'force'
            elif mass_rect.collidepoint(event.pos):
                input_active = 'mass'
            elif button_rect.collidepoint(event.pos):
                p_time = pygame.time.get_ticks()
                angle = angle_slider.get_current_value()
                force = force_slider.get_current_value()
                mass = mass_slider.get_current_value()
                dot_mass = mass
                v = calculate_velocity(angle, force, dot_mass)
                ball_launched = True
                dot_path = []
                dot_position = [spawn_x, spawn_y]
                goal_reached = False
                death_reached = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()

    # Clear screen
    screen.fill(BLACK)

    # Update GUI manager
    manager.update(time_delta)

    # Draw blocks
    for i in range(len(map)):
        for j in range(len(map[i])):
            b = map[i][j]
            if isinstance(b, Block):
                color = (b.friction * 255, 255, ((-1 * b.bounciness) + 1) * 255)
                pygame.draw.rect(screen, color, (
                    j * block_width, i * block_height, block_width, block_height))
            elif isinstance(b, Goal):
                # Render the goal as a semi-transparent green rectangle
                goal_surf = pygame.Surface((block_width, block_height))
                goal_surf.set_alpha(128)  # Set transparency to 50%
                goal_surf.fill(TRANSPARENT_GREEN)
                screen.blit(goal_surf, (j * block_width, i * block_height))
            elif isinstance(b, Death):
                death_surf = pygame.Surface((block_width, block_height))
                death_surf.set_alpha(128)  # Set transparency to 50%
                death_surf.fill(TRANSPARENT_RED)
                screen.blit(death_surf, (j * block_width, i * block_height))

    # Draw the path of the dot
    if len(dot_path) > 1:
        pygame.draw.lines(screen, WHITE, False, dot_path, 2)

    # Draw the dot
    pygame.draw.circle(screen, dot_color, [int(dot_position[0]), int(dot_position[1])], dot_radius)

    if goal_reached:
        transparent_surface_green = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        transparent_surface_green.fill(TRANSPARENT_GREEN)
        text = font.render('Goal Reached! Press R to restart', True, WHITE)
        screen.blit(transparent_surface_green, (0, 0))  # Blit the transparent surface
        screen.blit(text, (game_screen_width // 2 - text.get_width() // 2, game_screen_height // 2))

    if death_reached:
        transparent_surface_red = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        transparent_surface_red.fill(TRANSPARENT_RED)
        text = font.render('Game Over! Press R to restart', True, WHITE)
        screen.blit(transparent_surface_red, (0, 0))  # Blit the transparent surface
        screen.blit(text, (game_screen_width // 2 - text.get_width() // 2, game_screen_height // 2))

    if ball_launched and not goal_reached and not death_reached:
        # Calculate time between this frame and previous frame
        c_time = pygame.time.get_ticks()
        frametime = (c_time - p_time) / 1000
        p_time = c_time

        # Update the dot's position with the current velocity
        p_dot_position = dot_position.copy()
        dot_position[0] += v[0] * frametime
        dot_position[1] += v[1] * frametime

        # Append the current dot position to the path
        dot_path.append(dot_position.copy())

        # Apply gravity
        v[1] += g * frametime

        # Check for friction
        if v[1] == 0:  # The ball is on the ground
            block_width = game_screen_width // len(map[0])
            block_height = game_screen_height // len(map)

            column = int(dot_position[0] / block_width)
            row = int((dot_position[1] + dot_radius + 5) / block_height)  # Check the block directly underneath the ball

            if 0 <= column < len(map[0]) and 0 <= row < len(map):
                block = map[row][column]
                if isinstance(block, Block):
                    # Apply friction: v[0] -= block.friction * mass * g * frametime
                    friction_force = block.friction * dot_mass * g * frametime
                    if v[0] > 0:
                        v[0] = max(0, v[0] - friction_force)
                    else:
                        v[0] = min(0, v[0] + friction_force)

        # Check for collisions
        check_collision(dot_position, p_dot_position, map, v)

        # Screen bounds checking and handling
        if dot_position[0] < dot_radius:
            dot_position[0] = dot_radius
            v[0] = -v[0] * 0.8
        elif dot_position[0] > game_screen_width - dot_radius:
            dot_position[0] = game_screen_width - dot_radius
            v[0] = -v[0] * 0.8

        if dot_position[1] < dot_radius:
            dot_position[1] = dot_radius
            v[1] = -v[1] * 0.8
        elif dot_position[1] > game_screen_height - dot_radius:
            dot_position[1] = game_screen_height - dot_radius
            v[1] = -v[1] * 0.8

    # Draw GUI elements
    manager.draw_ui(screen)

    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()
