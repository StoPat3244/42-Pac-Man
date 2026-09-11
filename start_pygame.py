import pygame

from pacgums import draw_pac_gums, draw_super_pac_gums
from pacgums import generate_pac_gums, generate_super_pac_gums
from movements import can_move, move_pacman, draw_pacman
from eating import eat_pac_gum
from game_menu import main_menu

# walls
NORTH = 1   # bit 0
EAST = 2    # bit 1
SOUTH = 4    # bit 2
WEST = 8  # bit 3

def draw_maze(
    screen: pygame.Surface,
    maze: list[list[int]],
    cell_size: int,
    offset: tuple[int, int] = (0, 0),                   # point inside the frame from which to start drawing the maze
    wall_color: tuple[int, int, int] = (33, 79, 222),   # blue Pac-Man
    wall_thickness: int = 6,                            # thickness in pixel
) -> None:
    rows = len(maze)
    columns = len(maze[0]) if rows else 0

    if offset is None:
        # No offset given: center the maze inside the current screen.
        maze_pixel_width = columns * cell_size
        maze_pixel_height = rows * cell_size
        offset_x = (screen.get_width() - maze_pixel_width) // 2
        offset_y = (screen.get_height() - maze_pixel_height) // 2
    else:
        offset_x, offset_y = offset

    for row_idx, row in enumerate(maze):
        for col_idx, cell_value in enumerate(row):

            # for each cell, Computing the top-left corner of the cell in pixels
            x = offset_x + col_idx * cell_size
            y = offset_y + row_idx * cell_size

            # The 4 corners of the cell help us draw the 4 sides
            top_corner_sx = (x, y)
            top_corner_dx = (x + cell_size, y)
            bottom_corner_sx = (x, y + cell_size)
            bottom_corner_dx = (x + cell_size, y + cell_size)

            # we use the AND operator & to determine whether the wall exists or not
            if cell_value & NORTH:   # top of the cell
                pygame.draw.line(
                    screen, wall_color,
                    top_corner_sx, top_corner_dx,
                    wall_thickness
                )
            if cell_value & EAST:   # right side
                pygame.draw.line(
                    screen, wall_color,
                    top_corner_dx, bottom_corner_dx,
                    wall_thickness
                )
            if cell_value & SOUTH:   # bottom
                pygame.draw.line(
                    screen, wall_color,
                    bottom_corner_sx, bottom_corner_dx,
                    wall_thickness
                )
            if cell_value & WEST:   # eft side
                pygame.draw.line(
                    screen, wall_color,
                    top_corner_sx, bottom_corner_sx,
                    wall_thickness
                )


def draw_score(screen: pygame.Surface, score: int) -> None:
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))


def run_pygame(maze, pacgums: int) -> None:
    score = 0
    animation_timer = 0
    pacman_mouth_open = True
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    CELL_SIZE = 50       # pixel x cell, we can modify it
    rows = len(maze)
    columns = len(maze[0])
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Pac-Man")     # title of the frames

    # Initial frames
    if not main_menu(screen):
        pygame.quit()
        return

    clock_frames = pygame.time.Clock()        # create clock to control frames x second
    running = True
    super_pac_gums = generate_super_pac_gums(maze) # generate super pacgum location and avoiding pacgum location already generated
    pac_gums = generate_pac_gums(maze, pacgums, excluded_positions=super_pac_gums)

    # Initialize Pacman
    pacman_position = (1, 1)
    pacman_direction = "right"
    requested_direction = None

    movement_timer = 0
    movement_delay = 150  # milliseconds between movements

    pacman_open = pygame.image.load("pacman_open.png").convert_alpha()
    pacman_open = pygame.transform.scale(pacman_open, (CELL_SIZE, CELL_SIZE))

    pacman_closed = pygame.image.load("pacman_closed.png").convert_alpha()
    pacman_closed = pygame.transform.scale(pacman_closed, (CELL_SIZE, CELL_SIZE))

    while running:

        dt = clock_frames.tick(60)  # 60 frames x second (how many times this loop run per second)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    requested_direction = "up"

                elif event.key == pygame.K_DOWN:
                    requested_direction = "down"

                elif event.key == pygame.K_LEFT:
                    requested_direction = "left"

                elif event.key == pygame.K_RIGHT:
                    requested_direction = "right"

        # enables the animation of opening and closing pacman's mouth
        animation_timer += dt
        if animation_timer >= 200:
            animation_timer -= 200
            pacman_mouth_open = not pacman_mouth_open

        # automatic Pac-Man movement
        movement_timer += dt
        if movement_timer >= movement_delay:
            movement_timer -= movement_delay

            # Try to change to the requested direction
            if requested_direction is not None:
                if can_move(maze, pacman_position, requested_direction):
                    pacman_direction = requested_direction
                    requested_direction = None

            # Continue moving in the current direction
            if can_move(maze, pacman_position, pacman_direction):
                pacman_position = move_pacman(
                    maze,
                    pacman_position,
                    pacman_direction
                )

                if eat_pac_gum(pacman_position, pac_gums):
                    score += 10

                elif eat_pac_gum(pacman_position, super_pac_gums):
                    score += 20

        screen.fill((0, 0, 0))                   # background (RGB) color BLACK
        draw_maze(screen, maze, CELL_SIZE)    # prepare the frame
        draw_pac_gums(screen, pac_gums, CELL_SIZE) # Draws pac_gums in maze
        draw_super_pac_gums(screen, super_pac_gums, CELL_SIZE)

        if pacman_mouth_open:
            current_pacman_image = pacman_open
        else:
            current_pacman_image = pacman_closed

        draw_pacman(
            screen,
            pacman_position,
            current_pacman_image,
            CELL_SIZE,
            pacman_direction
        )

        draw_pacman(screen, pacman_position,
                    current_pacman_image, CELL_SIZE, pacman_direction)
        draw_score(screen, score)
        pygame.display.flip()                    # print the frame to the screen

    pygame.quit()
