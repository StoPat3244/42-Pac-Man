import pygame

from pacgums import draw_pac_gums, draw_super_pac_gums
from pacgums import generate_pac_gums, generate_super_pac_gums
from movements import Pacman
from eating import eat_pac_gum, eat_ghost
from game_menu import main_menu, game_over
from ghost import Ghost
from positions import find_center_position, find_corner_position

# from ghost import draw_ghost
# from ghost2 import move_ghost_bfs

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


def run_pygame(screen, maze, pacgums: int) -> None:
    score = 0
    CELL_SIZE = 80       # pixel x cell, we can modify it

    ghost1_scatter_targets = [
        find_corner_position(maze, "top_left"),
        find_corner_position(maze, "bottom_right"),
        find_corner_position(maze, "bottom_left"),
        find_corner_position(maze, "top_right"),
    ]

    ghost2_scatter_targets = [
        find_corner_position(maze, "bottom_left"),
        find_corner_position(maze, "top_left"),
        find_corner_position(maze, "top_right"),
        find_corner_position(maze, "bottom_right"),
    ]

    ghost3_scatter_targets = [
        find_corner_position(maze, "bottom_left"),
        find_corner_position(maze, "top_left"),
        find_corner_position(maze, "bottom_right"),
        find_corner_position(maze, "top_right"),
    ]

    ghost4_scatter_targets = [
        find_corner_position(maze, "bottom_right"),
        find_corner_position(maze, "top_right"),
        find_corner_position(maze, "top_left"),
        find_corner_position(maze, "bottom_left"),
    ]

    clock_frames = pygame.time.Clock()        # create clock to control frames x second
    running = True
    super_pac_gums = generate_super_pac_gums(maze) # generate super pacgum location and avoiding pacgum location already generated
    pac_gums = generate_pac_gums(maze, pacgums, excluded_positions=super_pac_gums)

    # Initialize Pacman and Ghosts in positions

    pacman_start = find_center_position(maze)

    ghost1_start = find_corner_position(maze, "top_left")

    ghost2_start = find_corner_position(maze, "top_right")

    ghost3_start = find_corner_position(maze, "bottom_left")

    ghost4_start = find_corner_position(maze, "bottom_right")

    # Initialize Pacman

    movement_timer = 0
    movement_delay = 200  # milliseconds between movements

    pacman_open = pygame.image.load("pacman_open.png").convert_alpha()
    pacman_open = pygame.transform.scale(pacman_open, (CELL_SIZE, CELL_SIZE))

    pacman_closed = pygame.image.load("pacman_closed.png").convert_alpha()
    pacman_closed = pygame.transform.scale(pacman_closed, (CELL_SIZE, CELL_SIZE))

    pacman = Pacman(position=pacman_start, open_image=pacman_open, closed_image=pacman_closed, cell_size=CELL_SIZE)

    # Initialize Ghosts with Algorithm
    ghost_timer = 0
    ghost_delay = 500

    ghost2_timer = 0
    ghost2_delay = 500

    ghost3_timer = 0
    ghost3_delay = 500

    ghost4_timer = 0
    ghost4_delay = 500

    frightened_timer = 0
    frightened_duration = 7000
    frightened_active = False

    ghost_image = pygame.image.load("ghost.png").convert_alpha()
    ghost_image = pygame.transform.scale(ghost_image, (CELL_SIZE, CELL_SIZE))

    ghost2_image = pygame.image.load("ghost1.png").convert_alpha()
    ghost2_image = pygame.transform.scale(ghost2_image, (CELL_SIZE, CELL_SIZE))

    ghost3_image = pygame.image.load("ghost2.png").convert_alpha()
    ghost3_image = pygame.transform.scale(ghost3_image, (CELL_SIZE, CELL_SIZE))

    ghost4_image = pygame.image.load("ghost1.png").convert_alpha()
    ghost4_image = pygame.transform.scale(ghost4_image, (CELL_SIZE, CELL_SIZE))

    ghost_sick = pygame.image.load("sick.png").convert_alpha()
    ghost_sick = pygame.transform.scale(ghost_sick, (CELL_SIZE, CELL_SIZE))

    ghost1 = Ghost(position=ghost1_start, image=ghost_image,
                   frightened_image=ghost_sick, cell_size=CELL_SIZE,
                   algorithm="a_star", scatter_targets=ghost1_scatter_targets)

    ghost2 = Ghost(position=ghost2_start, image=ghost2_image,
                   frightened_image=ghost_sick, cell_size=CELL_SIZE,
                   algorithm="bfs", scatter_targets=ghost2_scatter_targets)

    ghost3 = Ghost(position=ghost3_start, image=ghost3_image,
                   frightened_image=ghost_sick, cell_size=CELL_SIZE,
                   algorithm="bfs", scatter_targets=ghost3_scatter_targets)

    ghost4 = Ghost(position=ghost4_start, image=ghost4_image,
                   frightened_image=ghost_sick, cell_size=CELL_SIZE,
                   algorithm="bfs", scatter_targets=ghost4_scatter_targets)

    requested_direction = None

    while running:

        dt = clock_frames.tick(60)

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

        # Pac-Man animation
        pacman.update(dt)

        # frigtened timer

        if frightened_active:
            frightened_timer -= dt

            if frightened_timer <= 0:
                frightened_active = False

                ghost1.set_normal()
                ghost2.set_normal()
                ghost3.set_normal()
                ghost4.set_normal()

        # ghost1

        ghost_timer += dt

        if ghost_timer >= ghost_delay:
            ghost_timer -= ghost_delay

            ghost1.move(
                maze,
                pacman.position,
                ghost2.position,
                pacman.direction,
            )

        if ghost1.position == pacman.position:

            if ghost1.mode == "frightened":
                # Ghost gets eaten
                ghost1.position = (10, 10)

            else:
                # Pac-Man gets eaten
                running = False

        # Ghost2

        ghost2_timer += dt

        if ghost2_timer >= ghost2_delay:
            ghost2_timer -= ghost2_delay

            ghost2.move(
                maze,
                pacman.position,
                ghost1.position,
                pacman.direction,
            )

        if ghost2.position == pacman.position:

            if ghost2.mode == "frightened":
                # Ghost gets eaten
                ghost2.position = (10, 5)

            else:
                # Pac-Man gets eaten
                running = False


        # Ghost 3

        ghost3_timer += dt

        if ghost3_timer >= ghost3_delay:
            ghost3_timer -= ghost3_delay

            ghost3.move(
                maze,
                pacman.position,
                ghost2.position,
                pacman.direction,
            )

        if ghost3.position == pacman.position:

            if ghost3.mode == "frightened":
                # Ghost gets eaten
                ghost3.position = (10, 10)

            else:
                # Pac-Man gets eaten
                running = False


        # Ghost 4

        ghost4_timer += dt

        if ghost4_timer >= ghost4_delay:
            ghost4_timer -= ghost4_delay

            ghost4.move(
                maze,
                pacman.position,
                ghost3.position,
                pacman.direction,
            )

        if ghost4.position == pacman.position:

            if ghost4.mode == "frightened":
                # Ghost gets eaten
                ghost4.position = (10, 5)

            else:
                # Pac-Man gets eaten
                running = False


        # pacman movement

        movement_timer += dt

        if movement_timer >= movement_delay:
            movement_timer -= movement_delay

            # Try to change to requested direction
            if requested_direction is not None:

                if pacman.can_move(
                    maze,
                    requested_direction,
                ):
                    pacman.direction = requested_direction
                    requested_direction = None

            # Continue moving
            if pacman.can_move(
                maze,
                pacman.direction,
            ):
                pacman.move(
                    maze,
                    pacman.direction,
                )

                if eat_pac_gum(
                    pacman.position,
                    pac_gums,
                ):
                    score += 10

                elif eat_pac_gum(
                    pacman.position,
                    super_pac_gums,
                ):
                    score += 20

                    frightened_active = True
                    frightened_timer = frightened_duration

                    ghost1.set_frightened()
                    ghost2.set_frightened()
                    # ghost3.set_frightened()
                    # ghost4.set_frightened()

        screen.fill((0, 0, 0))

        draw_maze(
            screen,
            maze,
            CELL_SIZE,
        )

        draw_pac_gums(
            screen,
            pac_gums,
            CELL_SIZE,
        )

        draw_super_pac_gums(
            screen,
            super_pac_gums,
            CELL_SIZE,
        )

        pacman.draw(screen)

        ghost1.draw(screen)
        ghost2.draw(screen)
        ghost3.draw(screen)
        ghost4.draw(screen)

        draw_score(
            screen,
            score,
        )

        pygame.display.flip()
