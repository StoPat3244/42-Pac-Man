import pygame
import time
from pacgums import draw_pac_gums, draw_super_pac_gums
from pacgums import generate_pac_gums, generate_super_pac_gums
from movements import Pacman
from eating import eat_pac_gum, eat_ghost
#from game_menu import main_menu, game_over
from ghost import Ghost
from positions import find_center_position, find_corner_position
from mazegenerator import MazeGenerator

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


def load_images(cell_size: int) -> dict:
    return {
        "pacman_open": pygame.transform.scale(
            pygame.image.load("pacman_open.png").convert_alpha(), (cell_size, cell_size)
        ),
        "pacman_closed": pygame.transform.scale(
            pygame.image.load("pacman_closed.png").convert_alpha(), (cell_size, cell_size)
        ),
        "ghost1": pygame.transform.scale(
            pygame.image.load("ghost.png").convert_alpha(), (cell_size, cell_size)
        ),
        "ghost2": pygame.transform.scale(
            pygame.image.load("ghost1.png").convert_alpha(), (cell_size, cell_size)
        ),
        "ghost3": pygame.transform.scale(
            pygame.image.load("ghost2.png").convert_alpha(), (cell_size, cell_size)
        ),
        "ghost4": pygame.transform.scale(
            pygame.image.load("ghost1.png").convert_alpha(), (cell_size, cell_size)
        ),
        "ghost_sick": pygame.transform.scale(
            pygame.image.load("sick.png").convert_alpha(), (cell_size, cell_size)
        ),
    }


def setup_level(level, pacgums: int, images: dict, cell_size: int, seed=0) -> dict:
    """
    Builds a brand new maze (with its own width/height) plus every
    entity that depends on it: Pac-Man, the four ghosts, and the
    pac-gums. `level` is one Configuration.Level entry.
    """
    maze_gen = MazeGenerator((level.width, level.height), seed=seed)
    maze = maze_gen.maze

    super_pac_gums = generate_super_pac_gums(maze)
    pac_gums = generate_pac_gums(maze, pacgums, excluded_positions=super_pac_gums)

    pacman_start = find_center_position(maze)
    pacman = Pacman(
        start_position=pacman_start,
        position=pacman_start,
        open_image=images["pacman_open"],
        closed_image=images["pacman_closed"],
        cell_size=cell_size,
    )

    ghost1_start = find_corner_position(maze, "top_left")
    ghost2_start = find_corner_position(maze, "top_right")
    ghost3_start = find_corner_position(maze, "bottom_left")
    ghost4_start = find_corner_position(maze, "bottom_right")

    ghost1 = Ghost(position=ghost1_start, image=images["ghost1"],
                    frightened_image=images["ghost_sick"], cell_size=cell_size,
                    algorithm="a_star",
                    scatter_targets=[
                        find_corner_position(maze, "top_left"),
                        find_corner_position(maze, "bottom_right"),
                        find_corner_position(maze, "bottom_left"),
                        find_corner_position(maze, "top_right"),
                    ])
    ghost2 = Ghost(position=ghost2_start, image=images["ghost2"],
                    frightened_image=images["ghost_sick"], cell_size=cell_size,
                    algorithm="bfs",
                    scatter_targets=[
                        find_corner_position(maze, "bottom_left"),
                        find_corner_position(maze, "top_left"),
                        find_corner_position(maze, "top_right"),
                        find_corner_position(maze, "bottom_right"),
                    ])
    ghost3 = Ghost(position=ghost3_start, image=images["ghost3"],
                    frightened_image=images["ghost_sick"], cell_size=cell_size,
                    algorithm="bfs",
                    scatter_targets=[
                        find_corner_position(maze, "bottom_left"),
                        find_corner_position(maze, "top_left"),
                        find_corner_position(maze, "bottom_right"),
                        find_corner_position(maze, "top_right"),
                    ])
    ghost4 = Ghost(position=ghost4_start, image=images["ghost4"],
                    frightened_image=images["ghost_sick"], cell_size=cell_size,
                    algorithm="bfs",
                    scatter_targets=[
                        find_corner_position(maze, "bottom_right"),
                        find_corner_position(maze, "top_right"),
                        find_corner_position(maze, "top_left"),
                        find_corner_position(maze, "bottom_left"),
                    ])

    return {
        "maze": maze,
        "pacman": pacman,
        "pac_gums": pac_gums,
        "super_pac_gums": super_pac_gums,
        "ghosts": [
            (ghost1, ghost1_start),
            (ghost2, ghost2_start),
            (ghost3, ghost3_start),
            (ghost4, ghost4_start),
        ],
    }
def congratulations_screen(screen):
    font = pygame.font.Font(None, 80)
    text = font.render("CONGRATULATIONS!", True, (255, 255, 255))
    rect = text.get_rect(center=screen.get_rect().center)
    start_time = time.time()
    while time.time() - start_time < 5:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        screen.fill((0, 0, 0))
        screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.Clock().tick(60)


def define_cell_size(maze_size) -> int:
    width = maze_size.width
    height = maze_size.height + 6
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    cell_size = min( 80, screen_width // width,
        screen_height // height)
    return cell_size

def run_game(screen, config: "Configuration") -> int:
    score = 0
    level_index = 0
    CELL_SIZE = define_cell_size(config.level[level_index])
    #CELL_SIZE = 80

    images = load_images(CELL_SIZE)

    state = setup_level(config.level[level_index], config.pacgum, images, CELL_SIZE, config.seed)

    maze = state["maze"] # array of array
    pacman = state["pacman"] # object
    pac_gums = state["pac_gums"] # position
    super_pac_gums = state["super_pac_gums"] # position
    (ghost1, ghost1_start), (ghost2, ghost2_start), \
        (ghost3, ghost3_start), (ghost4, ghost4_start) = state["ghosts"] # position

    clock_frames = pygame.time.Clock()
    running = True

    movement_timer = 0
    movement_delay = 200

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
    requested_direction = None
# =========================== New variables for pause, lives, levels, and time ============================
    paused = False
    level_won = False
    level = 1
    start_time = pygame.time.get_ticks()
    paused_time = 0
    pause_start = None
    time_up = False
    level_max_time = config.level_max_time * 1000
    lives = config.lives
# ==============================================================================
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
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    running = False
        if not paused:
            pacman.update(dt)

            if frightened_active:
                frightened_timer -= dt
                if frightened_timer <= 0:
                    frightened_active = False
                    ghost1.set_normal()
                    ghost2.set_normal()
                    ghost3.set_normal()
                    ghost4.set_normal()

            ghost_timer += dt
            if ghost_timer >= ghost_delay:
                ghost_timer -= ghost_delay
                ghost1.move(maze, pacman.position, ghost2.position, pacman.direction)

            if ghost1.position == pacman.position:
                if ghost1.mode == "frightened":
                    ghost1.position = ghost1_start
                    ghost1.set_normal()
                else:
# ================================ Life Management ==============================
                    lives -= 1
                    pacman.position = pacman.start_position
                    ghost1.position = ghost1_start
                    ghost2.position = ghost2_start
                    ghost3.position = ghost3_start
                    ghost4.position = ghost4_start
# =========================================================================                    
                    if lives == 0:
                        running = False
            ghost2_timer += dt
            if ghost2_timer >= ghost2_delay:
                ghost2_timer -= ghost2_delay
                ghost2.move(maze, pacman.position, ghost1.position, pacman.direction)

            if ghost2.position == pacman.position:
                if ghost2.mode == "frightened":
                    ghost2.position = ghost2_start
                    ghost2.set_normal()
                else:
                    lives -= 1
                    pacman.position = pacman.start_position
                    ghost1.position = ghost1_start
                    ghost2.position = ghost2_start
                    ghost3.position = ghost3_start
                    ghost4.position = ghost4_start
                    if lives == 0:
                        running = False
            ghost3_timer += dt
            if ghost3_timer >= ghost3_delay:
                ghost3_timer -= ghost3_delay
                ghost3.move(maze, pacman.position, ghost2.position, pacman.direction)

            if ghost3.position == pacman.position:
                if ghost3.mode == "frightened":
                    ghost3.position = ghost3_start
                    ghost3.set_normal()
                else:
                    lives -= 1
                    pacman.position = pacman.start_position
                    ghost1.position = ghost1_start
                    ghost2.position = ghost2_start
                    ghost3.position = ghost3_start
                    ghost4.position = ghost4_start
                    if lives == 0:
                        running = False
            ghost4_timer += dt
            if ghost4_timer >= ghost4_delay:
                ghost4_timer -= ghost4_delay
                ghost4.move(maze, pacman.position, ghost3.position, pacman.direction)

            if ghost4.position == pacman.position:
                if ghost4.mode == "frightened":
                    ghost4.position = ghost4_start
                    ghost4.set_normal()
                else:
                    lives -= 1
                    pacman.position = pacman.start_position
                    ghost1.position = ghost1_start
                    ghost2.position = ghost2_start
                    ghost3.position = ghost3_start
                    ghost4.position = ghost4_start
                    if lives == 0:
                        running = False
            movement_timer += dt
            if movement_timer >= movement_delay:
                movement_timer -= movement_delay

                if requested_direction is not None:
                    if pacman.can_move(maze, requested_direction):
                        pacman.direction = requested_direction
                        requested_direction = None

                if pacman.can_move(maze, pacman.direction):
                    pacman.move(maze, pacman.direction)

                    if eat_pac_gum(pacman.position, pac_gums):
                        score += 10
                    elif eat_pac_gum(pacman.position, super_pac_gums):
                        score += 20
                        frightened_active = True
                        frightened_timer = frightened_duration
                        ghost1.set_frightened()
                        ghost2.set_frightened()
                        ghost3.set_frightened()
                        ghost4.set_frightened()

            screen.fill((0, 0, 0))
            draw_maze(screen, maze, CELL_SIZE)
            draw_pac_gums(screen, pac_gums, CELL_SIZE)
            draw_super_pac_gums(screen, super_pac_gums, CELL_SIZE)
            pacman.draw(screen)
            ghost1.draw(screen)
            ghost2.draw(screen)
            ghost3.draw(screen)
            ghost4.draw(screen)
            draw_score(screen, score)

            level_won = len(pac_gums) == 0
# ================================ Time Management ==============================            
            if pause_start is not None:
                paused_time += pygame.time.get_ticks() - pause_start
                pause_start = None
            elapsed_time = pygame.time.get_ticks() - start_time - paused_time
            if elapsed_time >= level_max_time:
                running = False

            font = pygame.font.Font(None, 36)
            remaining_time = max(0, (level_max_time - elapsed_time) // 1000)
            time_text = font.render(f"Time: {remaining_time}", True, (255, 255, 255))
            lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
            level_text = font.render(f"Level: {level}", True, (255, 255, 255))
            screen.blit(time_text, (100, 100))
            screen.blit(lives_text, (500, 500))
            screen.blit(level_text, (800, 800))
# ============================ PAUSE and ESC text =====================
            font = pygame.font.Font(None, 60)
            pause_instr_text = font.render("P = pause", True, (255, 255, 255))
            esc_instr_text = font.render("ESC = return to main menu", True, (255, 255, 255))
            rect_pause = pause_instr_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
            rect_esc = esc_instr_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 110))
            screen.blit(pause_instr_text, rect_pause)
            screen.blit(esc_instr_text, rect_esc)
# ================================ Pause Management ==============================        
        if paused:
            if pause_start is None:
                pause_start = pygame.time.get_ticks()
            font = pygame.font.Font(None, 60)
            pause_text = font.render("PAUSE\nPress P to continue", True, (255, 255, 255))
            rect = pause_text.get_rect(center=screen.get_rect().center)
            screen.blit(pause_text, rect)
# ================================ Level Management ==============================
        if level_won:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))

            font = pygame.font.Font(None, 60)
            level_won_text = font.render("LEVEL WON", True, (255, 255, 255))
            rect = level_won_text.get_rect(center=screen.get_rect().center)

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        level_index += 1
                        level += 1

                        if level_index >= len(config.level):
                            # No more levels defined: the player wins the whole game.
                            congratulations_screen(screen)
                            waiting = False
                            running = False

                        else:
                            CELL_SIZE = define_cell_size(config.level[level_index])
                            images = load_images(CELL_SIZE)
                            state = setup_level(
                                config.level[level_index], config.pacgum, images, CELL_SIZE
                            )

                            maze = state["maze"]
                            pacman = state["pacman"]
                            pac_gums = state["pac_gums"]
                            super_pac_gums = state["super_pac_gums"]
                            (ghost1, ghost1_start), (ghost2, ghost2_start), \
                                (ghost3, ghost3_start), (ghost4, ghost4_start) = state["ghosts"]

                            movement_timer = 0
                            ghost_timer = ghost2_timer = ghost3_timer = ghost4_timer = 0
                            frightened_active = False
                            level_won = False
                            running = True
                            waiting = False
                            lives = lives
                            start_time = pygame.time.get_ticks()
                            paused_time = 0
                            pause_start = None
                screen.blit(level_won_text, rect)
                pygame.display.flip()
        pygame.display.flip()

    return score
