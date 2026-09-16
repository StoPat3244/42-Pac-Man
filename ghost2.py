from collections import deque


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


def get_neighbors(maze, position):
    row, column = position
    cell = maze[row][column]

    neighbors = []

    if not (cell & NORTH) and row > 0:
        neighbors.append((row - 1, column))

    if not (cell & EAST) and column < len(maze[0]) - 1:
        neighbors.append((row, column + 1))

    if not (cell & SOUTH) and row < len(maze) - 1:
        neighbors.append((row + 1, column))

    if not (cell & WEST) and column > 0:
        neighbors.append((row, column - 1))

    return neighbors


def bfs(maze, start, target):
    if start == target:
        return [start]

    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()

        if current == target:
            path = [current]

            while came_from[current] is not None:
                current = came_from[current]
                path.append(current)

            path.reverse()
            return path

        for neighbor in get_neighbors(maze, current):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    return []


def predict_pacman_position(maze, pacman_position, pacman_direction, steps):
    position = pacman_position

    for _ in range(steps):
        row, column = position

        if pacman_direction == "up":
            direction = NORTH
        elif pacman_direction == "right":
            direction = EAST
        elif pacman_direction == "down":
            direction = SOUTH
        elif pacman_direction == "left":
            direction = WEST
        else:
            break

        cell = maze[row][column]

        if cell & direction:
            break

        if direction == NORTH:
            position = (row - 1, column)
        elif direction == EAST:
            position = (row, column + 1)
        elif direction == SOUTH:
            position = (row + 1, column)
        elif direction == WEST:
            position = (row, column - 1)

    return position


# def move_ghost_bfs(
#     maze,
#     ghost_position,
#     pacman_position,
#     pacman_direction
# ):
#     predicted_position = predict_pacman_position(
#         maze,
#         pacman_position,
#         pacman_direction,
#         steps=4
#     )

#     path = bfs(
#         maze,
#         ghost_position,
#         predicted_position
#     )

#     if len(path) < 2:
#         return ghost_position

#     return path[1]

def move_ghost_bfs(
    maze,
    ghost_position,
    pacman_position,
    pacman_direction,
    other_ghost_position
):
    predicted_position = predict_pacman_position(
        maze,
        pacman_position,
        pacman_direction,
        steps=4
    )

    path = bfs(
        maze,
        ghost_position,
        predicted_position
    )

    if len(path) < 2:
        return ghost_position

    next_position = path[1]

    if next_position == other_ghost_position:
        return ghost_position

    return next_position
