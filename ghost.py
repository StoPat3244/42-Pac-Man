import heapq
import pygame


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


def get_neighbors(
    maze: list[list[int]],
    position: tuple[int, int],
) -> list[tuple[int, int]]:
    row, column = position
    cell = maze[row][column]

    neighbors = []

    # Up
    if not (cell & NORTH):
        neighbors.append((row - 1, column))

    # Right
    if not (cell & EAST):
        neighbors.append((row, column + 1))

    # Down
    if not (cell & SOUTH):
        neighbors.append((row + 1, column))

    # Left
    if not (cell & WEST):
        neighbors.append((row, column - 1))

    return neighbors


def heuristic(
    position: tuple[int, int],
    target: tuple[int, int],
) -> int:
    row, column = position
    target_row, target_column = target

    return abs(row - target_row) + abs(column - target_column)


def a_star(
    maze: list[list[int]],
    start: tuple[int, int],
    target: tuple[int, int],
) -> list[tuple[int, int]]:

    if start == target:
        return [start]

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}

    g_score = {start: 0}

    while open_set:

        _, current = heapq.heappop(open_set)

        if current == target:
            path = [current]

            while current in came_from:
                current = came_from[current]
                path.append(current)

            path.reverse()
            return path

        for neighbor in get_neighbors(maze, current):

            # Ignore positions outside the maze
            row, column = neighbor

            if row < 0 or row >= len(maze):
                continue

            if column < 0 or column >= len(maze[0]):
                continue

            new_cost = g_score[current] + 1

            if (
                neighbor not in g_score
                or new_cost < g_score[neighbor]
            ):
                came_from[neighbor] = current
                g_score[neighbor] = new_cost

                f_score = new_cost + heuristic(
                    neighbor,
                    target
                )

                heapq.heappush(
                    open_set,
                    (f_score, neighbor)
                )

    # No path found
    return []


def draw_ghost(
    screen: pygame.Surface,
    ghost_position: tuple[int, int],
    ghost_image: pygame.Surface,
    cell_size: int,
) -> None:

    row, column = ghost_position

    x = column * cell_size
    y = row * cell_size

    screen.blit(
        ghost_image,
        (x, y)
    )
