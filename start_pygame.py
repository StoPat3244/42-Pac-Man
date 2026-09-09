import pygame

from pacgums import draw_pac_gums, draw_super_pac_gums, generate_pac_gums
from movements import can_move, move_pacman, draw_pacman

# walls
NORTH = 1   # bit 0
EAST = 2    # bit 1
SOUTH = 4    # bit 2
WEST = 8  # bit 3


def maze_from_txt_to_array(path: str) -> list[list[int]]:
    # Reads maze.txt and returns an array of arrays of integers ranging from 0 to 15 in hexadecimal
    grid = []
    with open(path) as f:
        for row in f:
            row = row.strip()
            if not row:
                continue
            # int(digit, 16) convert a .txt hexadecimal digit in int
            grid.append([int(digit, 16) for digit in row])
    return grid


def draw_maze(
    screen: pygame.Surface,
    maze: list[list[int]],
    cell_size: int,
    offset: tuple[int, int] = (0, 0),                   # point inside the frame from which to start drawing the maze
    wall_color: tuple[int, int, int] = (33, 79, 222),   # blue Pac-Man
    wall_thickness: int = 6,                            # thickness in pixel
) -> None:
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


def start_screen(screen, width, height):
    # load the image and resize it
    pacman_image = pygame.image.load("pacman.png").convert_alpha()
    width_image = width // 10
    height_image = height // 10
    pacman_image = pygame.transform.scale(pacman_image, (width_image, height_image))

    font = pygame.font.Font(None, 50)    # Font None = default font

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:     # if the User press any keys
                if event.key == pygame.K_RETURN:   # and if this key in ENTER
                    waiting = False                 # stop the presentation frames 

        # Background
        screen.fill((0, 0, 0))

        # Image Position
        image_x = (screen.get_width() - pacman_image.get_width()) // 2
        image_y = height // 8

        screen.blit(pacman_image, (image_x, image_y))    # copy image on surface for later print on screen (.flip) 

        # sentence
        text = font.render(
            "press ENTER for start the game",
            True,       # antialias, softer edges
            (255, 255, 255)
        )

        text_x = (screen.get_width() - text.get_width()) // 2
        text_y = height // 2

        screen.blit(text, (text_x, text_y))    # copy image on surface for later print on screen (.flip)

        pygame.display.flip()

    return True


def run_pygame(maze, pacgums: int) -> None:
    pygame.init()

    CELL_SIZE = 80       # pixel x cell, we can modify it

    # maze = maze_from_txt_to_array("maze.txt")
    rows = len(maze)
    columns = len(maze[0])

    width_window = columns * CELL_SIZE
    height_window = rows * CELL_SIZE

    screen = pygame.display.set_mode((width_window, height_window))
    pygame.display.set_caption("Test graphical maze - Pac-Man")     # title of the frames

    # Initial frames
    if not start_screen(screen, width_window, height_window):
        pygame.quit()
        return

    clock_frames = pygame.time.Clock()        # create clock to control frames x second
    running = True

    pac_gums = generate_pac_gums(maze, pacgums)
    nmb_superpacgums = len(pac_gums) // 10 # for every 10 pacgums there is one superpacgum
    super_pac_gums = generate_pac_gums(maze, nmb_superpacgums, excluded_positions=pac_gums,) # generate super pacgum location and avoiding pacgum location already generated

    # Initialize Pacman
    pacman_position = (1, 1)

    pacman_image = pygame.image.load("pacman.png").convert_alpha()

    pacman_image = pygame.transform.scale(pacman_image, (CELL_SIZE, CELL_SIZE))

    while running:
        for event in pygame.event.get():      # check the event
            if event.type == pygame.QUIT:     # check closing window
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    pacman_position = move_pacman(
                        maze,
                        pacman_position,
                        "up"
                    )

                elif event.key == pygame.K_DOWN:
                    pacman_position = move_pacman(
                        maze,
                        pacman_position,
                        "down"
                    )

                elif event.key == pygame.K_LEFT:
                    pacman_position = move_pacman(
                        maze,
                        pacman_position,
                        "left"
                    )

                elif event.key == pygame.K_RIGHT:
                    pacman_position = move_pacman(
                        maze,
                        pacman_position,
                        "right"
                    )

        screen.fill((0, 0, 0))                   # background (RGB) color BLACK
        draw_maze(screen, maze, CELL_SIZE)    # prepare the frame
        draw_pac_gums(screen, pac_gums, CELL_SIZE) # Draws pac_gums in maze
        draw_super_pac_gums(screen, super_pac_gums, CELL_SIZE)

        draw_pacman(screen, pacman_position, pacman_image, CELL_SIZE)

        pygame.display.flip()                    # print the frame to the screen
        clock_frames.tick(60)            # 60 frames x second (how many times this loop run per second)

    pygame.quit()
