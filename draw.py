import functools
from typing import Protocol
from pathlib import Path
import pygame

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# Wall bit flags used by the maze generator.
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
WALL_BLUE = (33, 79, 222)

# For each wall flag: (start corner, end corner) in unit-cell coordinates.
_WALLS = (
    (NORTH, (0, 0), (1, 0)),
    (EAST, (1, 0), (1, 1)),
    (SOUTH, (0, 1), (1, 1)),
    (WEST, (0, 0), (0, 1)),
)

_IMAGE_FILES = {
    "pacman_open": "pacman_open.png",
    "pacman_closed": "pacman_closed.png",
    "ghost1": "ghost.png",
    "ghost2": "ghost1.png",
    "ghost3": "ghost2.png",
    "ghost4": "ghost1.png",
    "ghost_sick": "sick.png",
}

@functools.lru_cache(maxsize=None)
def _font(size: int) -> pygame.font.Font:
    """Create each font size only once instead of every frame."""
    return pygame.font.Font(None, size)


def define_cell_size(width: int, height: int) -> int:
    """Largest cell (max 80 px) that fits the maze plus the HUD rows."""
    info = pygame.display.Info()
    height += 6 # six cells more for writing the infos (time, score, lives,...)
    return min(80, info.current_w // width, info.current_h // height)


def load_images(cell_size: int) -> dict[str, pygame.Surface]:
    size = (cell_size, cell_size)
    return {
        name: pygame.transform.scale(
            pygame.image.load(ASSETS_DIR / filename).convert_alpha(), size
        )
        for name, filename in _IMAGE_FILES.items()
    }


def draw_text(screen: pygame.Surface, text: str, size: int, position: tuple[int, int],
              color: list = WHITE) -> None:
    screen.blit(_font(size).render(text, True, color), position)


def draw_centered_text(screen: pygame.Surface, text: str, size: int, dy: int = 0,
                       color: list = WHITE) -> None:
    surface = _font(size).render(text, True, color)
    center = screen.get_rect().center
    rect = surface.get_rect(center=(center[0], center[1] + dy))
    screen.blit(surface, rect)


def draw_maze(screen: pygame.Surface, maze: list[list[int]], cell_size: int,
              offset: tuple[int, int] | None = (0, 0), wall_color: list = WALL_BLUE,
              wall_thickness: int = 6) -> None:
    rows = len(maze)
    columns = len(maze[0]) if rows else 0

    if offset is None:
        offset_x = (screen.get_width() - columns * cell_size) // 2
        offset_y = (screen.get_height() - rows * cell_size) // 2
    else:
        offset_x, offset_y = offset

    for row_idx, row in enumerate(maze):
        for col_idx, cell_value in enumerate(row):
            x = offset_x + col_idx * cell_size
            y = offset_y + row_idx * cell_size
            for flag, (sx, sy), (ex, ey) in _WALLS:
                if cell_value & flag:
                    pygame.draw.line(
                        screen,
                        wall_color,
                        (x + sx * cell_size, y + sy * cell_size),
                        (x + ex * cell_size, y + ey * cell_size),
                        wall_thickness,
                    )


def draw_game_info(screen: pygame.Surface, score: int, lives: int, level: int,
                   cell_size: int, cheat: bool, invincibility: bool, remaining_seconds: int, top: int) -> None:
    column_width = screen.get_width() // 4
    draw_text(screen, f"Lives: {lives}", cell_size, (10, top + cell_size))
    draw_text(screen, f"Time: {remaining_seconds}", cell_size, (10 + column_width, top + cell_size))
    draw_text(screen, f"Level: {level}", cell_size, (10, top + cell_size * 3))
    draw_text(screen, f"Score: {score}", cell_size, (10 + column_width, top + cell_size * 3))
    draw_text(screen, "P = pause", cell_size, (10, top + cell_size * 5))
    draw_text(screen, "ESC = main menu", cell_size, (10 + column_width, top + cell_size * 5))
    if cheat:
        draw_text(screen, "CHEAT MODE ACTIVED", cell_size, (10, top), YELLOW)
        draw_text(screen, "L : add live", cell_size, (10, top + cell_size * 2), YELLOW)
        draw_text(screen, "S : skip level", cell_size, (10, top + cell_size * 4), YELLOW)
        if invincibility:
            draw_text(screen, "I : invincibility ACTIVATED", cell_size, (10 + column_width, top), YELLOW)
        else:
            draw_text(screen, "I: invincibility DEactivated", cell_size, (10 + column_width, top), YELLOW)
    

def draw_pause(screen: pygame.Surface) -> None:
    draw_centered_text(screen, "PAUSE     Press P to continue", 60)


def draw_level_won(screen: pygame.Surface) -> None:
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))
    draw_centered_text(screen, "LEVEL WON", 60)
    draw_centered_text(screen, "Press SPACE to continue", 40, dy=60)


def draw_life_lost(screen: pygame.Surface) -> None:
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))
    draw_centered_text(screen, "LIFE LOST", 60)

def draw_time_finish(screen: pygame.Surface) -> None:
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))
    draw_centered_text(screen, "OUT OF TIME", 60)

def show_congratulations(screen: pygame.Surface, fps: int) -> None:
    clock = pygame.time.Clock()
    end = pygame.time.get_ticks() + 5000
    # Display the congratulations screen for five seconds
    while pygame.time.get_ticks() < end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(BLACK)
        draw_centered_text(screen, "YOU DID IT! PAC-MAN MASTER! GAME COMPLETE!", 80)
        pygame.display.flip()
        clock.tick(fps)
