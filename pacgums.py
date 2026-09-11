import pygame
import random


def generate_pac_gums(
    maze: list[list[int]],
    number_of_gums: int,
    excluded_positions: list[tuple[int, int]] | None = None,
) -> list[tuple[int, int]]:
    if excluded_positions is None:
        excluded_positions = []

    possible_positions = []

    for row_idx, row in enumerate(maze):
        for col_idx, cell_value in enumerate(row):
            if cell_value != 15:
                position = (row_idx, col_idx)

                if position not in excluded_positions:
                    possible_positions.append(position)

    if number_of_gums > len(possible_positions):
        raise ValueError(
            f"Cannot place {number_of_gums} Pac-Gums. "
            f"Only {len(possible_positions)} valid positions are available."
        )

    return random.sample(possible_positions, number_of_gums)


def draw_pac_gums(
    screen: pygame.Surface,
    pac_gums: list[tuple[int, int]],
    cell_size: int,
    offset: tuple[int, int] = (0, 0),
) -> None:
    offset_x, offset_y = offset

    for row, column in pac_gums:
        x = offset_x + column * cell_size
        y = offset_y + row * cell_size

        center_x = x + cell_size // 2
        center_y = y + cell_size // 2

        pygame.draw.circle(
            screen,
            (0, 255, 0),
            (center_x, center_y),
            5
        )


def generate_super_pac_gums(
    maze: list[list[int]],
) -> list[tuple[int, int]]:
    rows = len(maze)
    columns = len(maze[0])

    corners = [
        (0, 0),                  # top-left
        (0, columns - 1),        # top-right
        (rows - 1, 0),           # bottom-left
        (rows - 1, columns - 1), # bottom-right
    ]

    super_pac_gums = []

    for row, column in corners:
        if maze[row][column] != 15:
            super_pac_gums.append((row, column))

    return super_pac_gums


def draw_super_pac_gums(
    screen: pygame.Surface,
    super_pac_gums: list[tuple[int, int]],
    cell_size: int,
    offset: tuple[int, int] = (0, 0),
) -> None:
    offset_x, offset_y = offset

    for row, column in super_pac_gums:
        x = offset_x + column * cell_size
        y = offset_y + row * cell_size

        center_x = x + cell_size // 2
        center_y = y + cell_size // 2

        pygame.draw.circle(
            screen,
            (255, 0, 0),
            (center_x, center_y),
            12
        )
