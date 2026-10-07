import pygame
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


class Pacman:
    def __init__(
        self,
        start_position: tuple[int, int],
        position: tuple[int, int],
        open_image: pygame.Surface,
        closed_image: pygame.Surface,
        cell_size: int,
    ) -> None:
        self.start_position = start_position
        self.position = position
        self.open_image = open_image
        self.closed_image = closed_image
        self.cell_size = cell_size

        self.direction = "right"

        # Animation
        self.mouth_open = True
        self.animation_timer = 0
        self.animation_delay = 250

    def update(self, dt: int) -> None:
        """Update Pac-Man's mouth animation."""
        self.animation_timer += dt

        if self.animation_timer >= self.animation_delay:
            self.animation_timer -= self.animation_delay
            self.mouth_open = not self.mouth_open

    def can_move(
        self,
        maze: list[list[int]],
        direction: str,
    ) -> bool:
        row, column = self.position
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

    def move(
        self,
        maze: list[list[int]],
        direction: str,
    ) -> None:
        if not self.can_move(maze, direction):
            return

        row, column = self.position

        if direction == "up":
            row -= 1
        elif direction == "right":
            column += 1
        elif direction == "down":
            row += 1
        elif direction == "left":
            column -= 1

        self.position = (row, column)
        self.direction = direction

    def draw(self, screen: pygame.Surface) -> None:
        row, column = self.position

        x = column * self.cell_size
        y = row * self.cell_size

        # Select the current animation frame
        if self.mouth_open:
            pacman_image = self.open_image
        else:
            pacman_image = self.closed_image

        # Adjust image according to direction
        if self.direction == "left":
            pacman_image = pygame.transform.flip(
                pacman_image,
                True,
                False,
            )

        elif self.direction == "up":
            pacman_image = pygame.transform.rotate(
                pacman_image,
                90,
            )

        elif self.direction == "down":
            pacman_image = pygame.transform.rotate(
                pacman_image,
                -90,
            )

        screen.blit(pacman_image, (x, y))
