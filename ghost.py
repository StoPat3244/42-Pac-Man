import heapq
from collections import deque

import pygame


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


class Ghost:
    def __init__(
        self,
        position: tuple[int, int],
        image: pygame.Surface,
        frightened_image: pygame.Surface,
        cell_size: int,
        algorithm: str,
        scatter_targets
    ) -> None:
        self.position = position
        self.normal_image = image
        self.frightened_image = frightened_image
        self.image = self.normal_image
        self.cell_size = cell_size
        self.algorithm = algorithm
        self.mode = "scatter"
        self.scatter_targets = scatter_targets
        self.scatter_target_index = 0

    def get_neighbors(
        self,
        maze: list[list[int]],
        position: tuple[int, int],
    ) -> list[tuple[int, int]]:
        row, column = position
        cell = maze[row][column]

        neighbors = []

        # Up
        if not (cell & NORTH) and row > 0:
            neighbors.append((row - 1, column))

        # Right
        if not (cell & EAST) and column < len(maze[0]) - 1:
            neighbors.append((row, column + 1))

        # Down
        if not (cell & SOUTH) and row < len(maze) - 1:
            neighbors.append((row + 1, column))

        # Left
        if not (cell & WEST) and column > 0:
            neighbors.append((row, column - 1))

        return neighbors

    def heuristic(
        self,
        position: tuple[int, int],
        target: tuple[int, int],
    ) -> int:
        row, column = position
        target_row, target_column = target

        return abs(row - target_row) + abs(column - target_column)

    def a_star(
        self,
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

            for neighbor in self.get_neighbors(maze, current):

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

                    f_score = new_cost + self.heuristic(
                        neighbor,
                        target,
                    )

                    heapq.heappush(
                        open_set,
                        (f_score, neighbor),
                    )

        return []

    def bfs(
        self,
        maze: list[list[int]],
        start: tuple[int, int],
        target: tuple[int, int],
    ) -> list[tuple[int, int]]:

        if start == target:
            return [start]

        queue = deque([start])

        came_from = {
            start: None
        }

        while queue:

            current = queue.popleft()

            if current == target:

                path = [current]

                while came_from[current] is not None:
                    current = came_from[current]
                    path.append(current)

                path.reverse()
                return path

            for neighbor in self.get_neighbors(
                maze,
                current,
            ):
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return []

    def predict_pacman_position(
        self,
        maze: list[list[int]],
        pacman_position: tuple[int, int],
        pacman_direction: str,
        steps: int,
    ) -> tuple[int, int]:

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

    def distance_to_pacman(self, pacman_position):
        row, column = self.position
        pacman_row, pacman_column = pacman_position

        return abs(row - pacman_row) + abs(column - pacman_column)

    def move(
        self,
        maze: list[list[int]],
        pacman_position: tuple[int, int],
        other_ghost_position: tuple[int, int],
        pacman_direction: str | None = None,
    ) -> None:

        if self.mode == "frightened":
            self.frightened(maze, pacman_position)
            return

        distance = self.distance_to_pacman(pacman_position)

        if distance <= 7:
            self.mode = "chase"
        else:
            self.mode = "scatter"

        if self.mode == "scatter":
            self.scatter(maze)

        elif self.mode == "chase":
            self.chase(
                maze,
                pacman_position,
                other_ghost_position,
                pacman_direction,
            )

    def draw(
        self,
        screen: pygame.Surface,
    ) -> None:

        row, column = self.position

        x = column * self.cell_size
        y = row * self.cell_size

        screen.blit(
            self.image,
            (x, y),
        )

    def scatter(self, maze):
        target = self.scatter_targets[self.scatter_target_index]

        path = self.a_star(
            maze,
            self.position,
            target,
        )

        if len(path) < 2:
            # We reached the current target.
            self.scatter_target_index = (
                self.scatter_target_index + 1
            ) % len(self.scatter_targets)

            return

        self.position = path[1]

    def chase(
        self,
        maze: list[list[int]],
        pacman_position: tuple[int, int],
        other_ghost_position: tuple[int, int],
        pacman_direction: str | None = None,
    ) -> None:

        if self.algorithm == "a_star":

            target = pacman_position

            path = self.a_star(
                maze,
                self.position,
                target,
            )

        elif self.algorithm == "bfs":

            if pacman_direction is None:
                return

            target = self.predict_pacman_position(
                maze,
                pacman_position,
                pacman_direction,
                steps=4,
            )

            path = self.bfs(
                maze,
                self.position,
                target,
            )

        else:
            raise ValueError(
                f"Unknown ghost algorithm: {self.algorithm}"
            )

        if len(path) < 2:
            return

        next_position = path[1]

        # Prevent the ghosts from moving into each other.
        if next_position == other_ghost_position:
            return

        self.position = next_position

    def frightened(
        self,
        maze: list[list[int]],
        pacman_position: tuple[int, int],
    ) -> None:

        neighbors = self.get_neighbors(
            maze,
            self.position,
        )

        if not neighbors:
            return

        # Choose the neighbor that is furthest away
        # from Pac-Man using Manhattan distance.
        next_position = max(
            neighbors,
            key=lambda position: self.heuristic(
                position,
                pacman_position,
            ),
        )

        self.position = next_position

    def set_frightened(self) -> None:
        self.mode = "frightened"
        self.image = self.frightened_image

    def set_normal(self) -> None:
        self.mode = "scatter"
        self.image = self.normal_image
