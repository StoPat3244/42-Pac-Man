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
            (255, 255, 255),
            (center_x, center_y),
            5
        )


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
            (255, 255, 255),
            (center_x, center_y),
            12
        )
        