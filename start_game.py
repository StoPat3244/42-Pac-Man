# senza toccare i ghost
import pygame
import time
import draw
import sys
from pacgums import draw_pac_gums, draw_super_pac_gums
from pacgums import generate_pac_gums, generate_super_pac_gums
from movements import Pacman
from eating import eat_pac_gum, eat_ghost
#from game_menu import main_menu, game_over
from ghost import Ghost
from positions import find_center_position, find_corner_position
from mazegenerator import MazeGenerator
from configuration import Configuration

# from ghost import draw_ghost
# from ghost2 import move_ghost_bfs
class Game:
    FPS = 60    # frame per second
    # Per-level state, (re)filled by _load_level().
    cell_size: int
    images: dict
    maze: list[list[int]]
    pacman: Pacman
    pac_gums: list[tuple[int, int]]
    super_pac_gums: list[tuple[int, int]]
    movement_timer: int
    frightened_active: bool
    level_won: bool
    start_time: int
    paused_time: int
    pause_start: int | None

    def __init__(self, screen: pygame.Surface,
                 config: Configuration) -> None:
        self.screen = screen
        self.config = config
        self.clock_frames = pygame.time.Clock()
        self.running = True

        # Whole-game state.
        self.cheat_mode = config.cheat_mode
        self.score = 0
        self.lives = config.lives
        self.level_index = 0
        self.level = 1
        self.level_max_time = config.level_max_time * 1000
        self.points_per_pacgum = config.points_per_pacgum
        self.points_per_super_pacgum = config.points_per_super_pacgum

        # Pac-Man movement, frightened mode, pause.
        self.movement_delay = 200
        self.frightened_timer = 0
        self.frightened_duration = 7000
        self.requested_direction: str | None = None
        self.paused = False

    
    def _show_congratulations(self) -> None:
        end = pygame.time.get_ticks() + 5000
        while pygame.time.get_ticks() < end:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            draw.draw_congratulations(self.screen)
            pygame.display.flip()
            self.clock_frames.tick(self.FPS)
    
    def _load_level(self, seed=0) -> dict:
        level = self.config.level[self.level_index]
        self.cell_size = draw.define_cell_size(level)
        self.images = draw.load_images(self.cell_size)

        self.maze = MazeGenerator((level.width, level.height), seed=seed).maze
        self.super_pac_gums = generate_super_pac_gums(self.maze)
        self.pac_gums = generate_pac_gums(
            self.maze, self.config.pacgum,
            excluded_positions=self.super_pac_gums,
        )

        pacman_start = find_center_position(self.maze)
        self.pacman = Pacman(
            start_position=pacman_start,
            position=pacman_start,
            open_image=self.images["pacman_open"],
            closed_image=self.images["pacman_closed"],
            cell_size=self.cell_size,
        )

        ghost1_start = find_corner_position(self.maze, "top_left")
        ghost2_start = find_corner_position(self.maze, "top_right")
        ghost3_start = find_corner_position(self.maze, "bottom_left")
        ghost4_start = find_corner_position(self.maze, "bottom_right")

        ghost1 = Ghost(position=ghost1_start, image=self.images["ghost1"],
                        frightened_image=self.images["ghost_sick"], cell_size=self.cell_size,
                        algorithm="a_star",
                        scatter_targets=[
                            find_corner_position(self.maze, "top_left"),
                            find_corner_position(self.maze, "bottom_right"),
                            find_corner_position(self.maze, "bottom_left"),
                            find_corner_position(self.maze, "top_right"),
                        ])
        ghost2 = Ghost(position=ghost2_start, image=self.images["ghost2"],
                        frightened_image=self.images["ghost_sick"], cell_size=self.cell_size,
                        algorithm="bfs",
                        scatter_targets=[
                            find_corner_position(self.maze, "bottom_left"),
                            find_corner_position(self.maze, "top_left"),
                            find_corner_position(self.maze, "top_right"),
                            find_corner_position(self.maze, "bottom_right"),
                        ])
        ghost3 = Ghost(position=ghost3_start, image=self.images["ghost3"],
                        frightened_image=self.images["ghost_sick"], cell_size=self.cell_size,
                        algorithm="bfs",
                        scatter_targets=[
                            find_corner_position(self.maze, "bottom_left"),
                            find_corner_position(self.maze, "top_left"),
                            find_corner_position(self.maze, "bottom_right"),
                            find_corner_position(self.maze, "top_right"),
                        ])
        ghost4 = Ghost(position=ghost4_start, image=self.images["ghost4"],
                        frightened_image=self.images["ghost_sick"], cell_size=self.cell_size,
                        algorithm="bfs",
                        scatter_targets=[
                            find_corner_position(self.maze, "bottom_right"),
                            find_corner_position(self.maze, "top_right"),
                            find_corner_position(self.maze, "top_left"),
                            find_corner_position(self.maze, "bottom_left"),
                        ])
        self.movement_timer = 0
        self.frightened_active = False
        self.level_won = False
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.pause_start = None
        return [
            (ghost1, ghost1_start),
            (ghost2, ghost2_start),
            (ghost3, ghost3_start),
            (ghost4, ghost4_start)
            ]


    def run(self) -> int:
        (ghost1, ghost1_start), (ghost2, ghost2_start), \
            (ghost3, ghost3_start), (ghost4, ghost4_start) = \
            self._load_level(self.config.seed)
        ghost_timer = 0
        ghost_delay = 500
        ghost2_timer = 0
        ghost2_delay = 500
        ghost3_timer = 0
        ghost3_delay = 500
        ghost4_timer = 0
        ghost4_delay = 500

        while self.running:
            dt = self.clock_frames.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.requested_direction = "up"
                    elif event.key == pygame.K_DOWN:
                        self.requested_direction = "down"
                    elif event.key == pygame.K_LEFT:
                        self.requested_direction = "left"
                    elif event.key == pygame.K_RIGHT:
                        self.requested_direction = "right"
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_s and self.cheat_mode == True:
                        self.level_won = True
            if not self.paused and not self.level_won:
                self.pacman.update(dt)

                if self.frightened_active:
                    self.frightened_timer -= dt
                    if self.frightened_timer <= 0:
                        self.frightened_active = False
                        ghost1.set_normal()
                        ghost2.set_normal()
                        ghost3.set_normal()
                        ghost4.set_normal()

                ghost_timer += dt
                if ghost_timer >= ghost_delay:
                    ghost_timer -= ghost_delay
                    ghost1.move(self.maze, self.pacman.position,
                                ghost2.position, self.pacman.direction)

                if ghost1.position == self.pacman.position and self.cheat_mode == False:
                    if ghost1.mode == "frightened":
                        ghost1.position = ghost1_start
                        ghost1.set_normal()
                    else:
                        self.lives -= 1
                        self.pacman.position = self.pacman.start_position
                        ghost1.position = ghost1_start
                        ghost2.position = ghost2_start
                        ghost3.position = ghost3_start
                        ghost4.position = ghost4_start
                        if self.lives == 0:
                            self.running = False
                ghost2_timer += dt
                if ghost2_timer >= ghost2_delay:
                    ghost2_timer -= ghost2_delay
                    ghost2.move(self.maze, self.pacman.position,
                                ghost1.position, self.pacman.direction)

                if ghost2.position == self.pacman.position and self.cheat_mode == False:
                    if ghost2.mode == "frightened":
                        ghost2.position = ghost2_start
                        ghost2.set_normal()
                    else:
                        self.lives -= 1
                        self.pacman.position = self.pacman.start_position
                        ghost1.position = ghost1_start
                        ghost2.position = ghost2_start
                        ghost3.position = ghost3_start
                        ghost4.position = ghost4_start
                        if self.lives == 0:
                            self.running = False
                ghost3_timer += dt
                if ghost3_timer >= ghost3_delay:
                    ghost3_timer -= ghost3_delay
                    ghost3.move(self.maze, self.pacman.position,
                                ghost2.position, self.pacman.direction)

                if ghost3.position == self.pacman.position and self.cheat_mode == False:
                    if ghost3.mode == "frightened":
                        ghost3.position = ghost3_start
                        ghost3.set_normal()
                    else:
                        self.lives -= 1
                        self.pacman.position = self.pacman.start_position
                        ghost1.position = ghost1_start
                        ghost2.position = ghost2_start
                        ghost3.position = ghost3_start
                        ghost4.position = ghost4_start
                        if self.lives == 0:
                            self.running = False
                ghost4_timer += dt
                if ghost4_timer >= ghost4_delay:
                    ghost4_timer -= ghost4_delay
                    ghost4.move(self.maze, self.pacman.position,
                                ghost3.position, self.pacman.direction)

                if ghost4.position == self.pacman.position and self.cheat_mode == False:
                    if ghost4.mode == "frightened":
                        ghost4.position = ghost4_start
                        ghost4.set_normal()
                    else:
                        self.lives -= 1
                        self.pacman.position = self.pacman.start_position
                        ghost1.position = ghost1_start
                        ghost2.position = ghost2_start
                        ghost3.position = ghost3_start
                        ghost4.position = ghost4_start
                        if self.lives == 0:
                            self.running = False
                # ===== end of ghost code =====

                self.movement_timer += dt
                if self.movement_timer >= self.movement_delay:
                    self.movement_timer -= self.movement_delay

                    if self.requested_direction is not None:
                        if self.pacman.can_move(self.maze,
                                                self.requested_direction):
                            self.pacman.direction = self.requested_direction
                            self.requested_direction = None

                    if self.pacman.can_move(self.maze,
                                            self.pacman.direction):
                        self.pacman.move(self.maze, self.pacman.direction)

                        if eat_pac_gum(self.pacman.position, self.pac_gums):
                            self.score += self.points_per_pacgum
                        elif eat_pac_gum(self.pacman.position,
                                         self.super_pac_gums):
                            self.score += self.points_per_super_pacgum
                            self.frightened_active = True
                            self.frightened_timer = self.frightened_duration
                            ghost1.set_frightened()
                            ghost2.set_frightened()
                            ghost3.set_frightened()
                            ghost4.set_frightened()

                self.screen.fill((0, 0, 0))
                draw.draw_maze(self.screen, self.maze, self.cell_size)
                draw_pac_gums(self.screen, self.pac_gums, self.cell_size)
                draw_super_pac_gums(self.screen, self.super_pac_gums,
                                    self.cell_size)
                self.pacman.draw(self.screen)
                ghost1.draw(self.screen)
                ghost2.draw(self.screen)
                ghost3.draw(self.screen)
                ghost4.draw(self.screen)
                #draw_score(self.screen, self.score)

                self.level_won = len(self.pac_gums) == 0
# ============================ Time Management ============================
                if self.pause_start is not None:
                    self.paused_time += (
                        pygame.time.get_ticks() - self.pause_start
                    )
                    self.pause_start = None
                elapsed_time = (pygame.time.get_ticks()
                                - self.start_time - self.paused_time)
                if elapsed_time >= self.level_max_time:
                    self.running = False

                remaining_time = max(
                    0, (self.level_max_time - elapsed_time) // 1000
                )
                xy_top = len(self.maze) * self.cell_size + self.cell_size
                draw.draw_game_info(self.screen, self.score, self.lives,
                              self.level_index + 1, self.cell_size, self.cheat_mode,
                              remaining_time, xy_top)
# ========================= PAUSE and ESC text ============================
            if self.paused:
                if self.pause_start is None:
                    self.pause_start = pygame.time.get_ticks()
                draw.draw_pause(self.screen)
# ============================ Level Management ===========================
            if self.level_won:
                draw.draw_level_won(self.screen)
                pygame.display.flip()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if (event.type == pygame.KEYDOWN
                                and event.key == pygame.K_SPACE):
                            self.level_index += 1
                            if self.level_index >= len(self.config.level):
                                # No more levels defined: the player wins the whole game.
                                self._show_congratulations()
                                waiting = False
                            else:
                                (ghost1, ghost1_start), \
                                (ghost2, ghost2_start), \
                                (ghost3, ghost3_start), \
                                (ghost4, ghost4_start) = \
                                self._load_level()
                                ghost_timer = ghost2_timer = 0
                                ghost3_timer = ghost4_timer = 0
                                waiting = False
                    self.clock_frames.tick(self.FPS)
# ============================================================
            pygame.display.flip()

        return self.score
