import pygame

NORTH = 1   # bit 0
EAST = 2    # bit 1
SOUTH = 4    # bit 2
WEST = 8  # bit 3


def move_pacman(
    maze: list[list[int]],
    position: tuple[int, int],
    direction: str,
) -> tuple[int, int]:

    row, column = position

    if not can_move(maze, position, direction):
        return position

    if direction == "up":
        row -= 1
    elif direction == "right":
        column += 1
    elif direction == "down":
        row += 1
    elif direction == "left":
        column -= 1

    return row, column


def draw_pacman(
    screen: pygame.Surface,
    pacman_position: tuple[int, int],
    pacman_image: pygame.Surface,
    cell_size: int,
    direction: str,
) -> None:
    row, column = pacman_position
    x = column * cell_size
    y = row * cell_size

    if direction == "left":  # Image is not rotated but instead mirrored since if it is rotated, it will be upside down
        pacman_image = pygame.transform.flip(
            pacman_image,
            True,   # flip horizontally
            False   # don't flip vertically
        )

    elif direction == "up":
        pacman_image = pygame.transform.rotate(
            pacman_image,
            90
        )

    elif direction == "down":
        pacman_image = pygame.transform.rotate(
            pacman_image,
            -90
        )

    screen.blit(pacman_image, (x, y))


def can_move(
    maze: list[list[int]],
    position: tuple[int, int],
    direction: str,
) -> bool:

    row, column = position
    cell = maze[row][column]

    if direction == "up":
        return not (cell & NORTH)

    if direction == "right":
        return not (cell & EAST)

    if direction == "down":
        return not (cell & SOUTH)

    if direction == "left":
        return not (cell & WEST)

    return False

