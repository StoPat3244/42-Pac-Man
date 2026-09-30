import sys
import pygame
import time
from configuration import Configuration
import draw
from eating import eat_pac_gum
from ghost import Ghost
from mazegenerator import MazeGenerator
from movements import Pacman
from pacgums import draw_pac_gums, draw_super_pac_gums
from pacgums import generate_pac_gums, generate_super_pac_gums
from positions import find_center_position, find_corner_position

# Dictionary for each ghost setup: starting corner, algorithm, image, targets corners for scatter mode
GHOST_SETS = [
    {"corner": "top_left", "algo": "a_star", "image": "ghost1",
     "target": ["top_left", "bottom_right", "bottom_left", "top_right"]},
    {"corner": "top_right", "algo": "bfs", "image": "ghost2",
    "target": ["bottom_left", "top_left", "top_right", "bottom_right"]},
    {"corner": "bottom_left", "algo": "bfs", "image": "ghost3",
    "target": ["bottom_left", "top_left", "bottom_right", "top_right"]},
    {"corner": "bottom_right", "algo": "bfs", "image": "ghost4",
    "target": ["bottom_right", "top_right", "top_left", "bottom_left"]},
]


class Game:
    FPS = 60    # frame per second
    MOVE_DELAY = 200            # ms between Pac-Man steps
    GHOST_DELAY = 500           # ms between ghost steps
    FRIGHTENED_DURATION = 7000

    # Variables that changes from level to level (filled by _load_level).
    maze: list[list[int]]
    cell_size: int
    images: dict[str, pygame.Surface]
    pacman: Pacman
    pac_gums: list[tuple[int, int]]
    super_pac_gums: list[tuple[int, int]]
    ghosts: list[Ghost] # list of 4 Ghost objects

    def __init__(self, screen: pygame.Surface, config: Configuration):
        self.screen = screen # Pygame scren
        self.config = config # object Configuration
        self.clock = pygame.time.Clock() # to control the game speed and calculate elapsed time

        # Variables that remane for the whole game.
        self.cheat_mode = config.cheat_mode
        self.score = 0
        self.lives = config.lives
        self.level_index = 0
        self.level_max_time = config.level_max_time * 1000 # time in seconds printed on screen
        self.points_per_pacgum = config.points_per_pacgum
        self.points_per_super_pacgum = config.points_per_super_pacgum
        self.points_per_ghost = config.points_per_ghost
        self.running = True
        self.invincibility = False # flag for cheat_mode
        self.life_lost = False
        self._load_level(config.seed) # generate the first level with seed
    
    def _load_level(self, seed: int | str = 0) -> None:
        level = self.config.level[self.level_index] # get width and height of the maze
        self.cell_size = draw.define_cell_size(level.width, level.height) # define cell_size
        self.images = draw.load_images(self.cell_size) # load all the images
        # generate Maze
        self.maze = MazeGenerator((level.width, level.height), seed=seed).maze
        # generate super_pac_gums
        self.super_pac_gums = generate_super_pac_gums(self.maze)
        # generate pac_gums
        self.pac_gums = generate_pac_gums(self.maze, self.config.pacgum,
                                          excluded_positions=self.super_pac_gums)
        # generate pac_man in the center of the maze
        start = find_center_position(self.maze) 
        self.pacman = Pacman(start_position=start, position=start, open_image=self.images["pacman_open"],
                             closed_image=self.images["pacman_closed"], cell_size=self.cell_size)

        def _generate_ghosts():
            ghosts = []
            for ghost in GHOST_SETS:
                start_position = find_corner_position(self.maze, ghost["corner"])
                ghosts.append(Ghost(
                    position=start_position,
                    start_position=start_position,
                    image=self.images[ghost["image"]],
                    frightened_image=self.images["ghost_sick"],
                    cell_size=self.cell_size,
                    algorithm=ghost["algo"],
                    scatter_targets=[
                        find_corner_position(self.maze, corner)
                        for corner in ghost["target"]
                    ],
                ))
            return ghosts
        self.ghosts = _generate_ghosts()
        
        self.movement_timer = 0 # timer for pac_man movement
        self.frightened_timer = 0
        self.frightened_active = False
        self.requested_direction: str | None = None
        self.paused = False
        self.level_won = False
        self.start_time = time.monotonic() # variable for pause mode
        self.paused_time = 0 # variable for pause mode
        self.pause_start: int | None = None # flag for pause mode

    def _next_level(self) -> None:
        """Move to the next level or finish the game."""
        self.level_index += 1
        # If there are no more levels, show the final screen.
        if self.level_index >= len(self.config.level):
            draw.show_congratulations(self.screen, self.FPS)
            self.running = False
        else: # otherwise, generate the next level
            self._load_level() # generate the next without seed


    def _update_ghosts(self, dt: int) -> None:
        """Update ghost positions and check for collisions with Pac-Man."""
        for i, ghost in enumerate(self.ghosts): # for each ghost in the list
            ghost.ghost_timer += dt # increase the timer
            if ghost.ghost_timer >= self.GHOST_DELAY: # if it is time to move:
                ghost.ghost_timer -= self.GHOST_DELAY # update the time
                # move the ghost
                ghost.move(self.maze, self.pacman.position,
                           self.ghosts[(i + 1) // len(self.ghosts)].position, self.pacman.direction)
            if ghost.position == self.pacman.position: # if the ghost is in the same cell of pacman
                self._collision_ghost_pacman(i) # check if the ghost can eat the pacman
                if not self.running:
                    return

    def _collision_ghost_pacman(self, index: int) -> None:
        ghost = self.ghosts[index]
        if ghost.mode == "frightened":
            self.score += self.points_per_ghost
            ghost.position = ghost.start_position  # return the ghost to the start position
            ghost.set_normal()  # ghost return in scatter mode
        else:
            if self.invincibility == False: # check cheat mode
                for ghost in self.ghosts:
                    ghost.draw(self.screen)
                pygame.display.flip()
                self.lives -= 1
                self.life_lost = True
                if self.lives <= 0:
                    self.running = False   
            else:
                return
    
    def run(self) -> int:
        """Run the main game loop and return the final score."""
        while self.running:

            dt = self.clock.tick(self.FPS)

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
                    elif event.key == pygame.K_p: # pause
                        self.paused = not self.paused
                    elif event.key == pygame.K_ESCAPE: # esc
                        self.running = False
                    # ========= only for cheat mode ============================
                    elif event.key == pygame.K_s and self.cheat_mode == True:
                        self.level_won = True # skip level
                    elif event.key == pygame.K_l and self.cheat_mode == True:
                        self.lives += 1 # add lives
                        self._draw_during_pause(remaining_time, y_top)
                    elif event.key == pygame.K_i and self.cheat_mode == True:
                        # invincibility on-off
                        self.invincibility = not self.invincibility 
                        self._draw_during_pause(remaining_time, y_top)

        # ===== FIRST BIG PART = NOT PAUSED ========================= 

            # Game objects are updated only when the game is not paused           
            if not self.paused and not self.level_won:
                # ======================== GHOST ============================  
                # check ghosts state and update it      
                if self.frightened_active:
                    self.frightened_timer -= dt
                    if self.frightened_timer <= 0: 
                        self.frightened_active = False
                        for ghost in self.ghosts:
                            ghost.set_normal()

                self._update_ghosts(dt) # ghost position and check EATING PACMAN

                # ======================= PAC-MAN ======================================
                self.movement_timer += dt  # pac-man moves only after MOVE_DELAY
                if self.movement_timer >= self.MOVE_DELAY:
                    self.movement_timer -= self.MOVE_DELAY

                    wanted = self.requested_direction
                    # Apply the player's requested direction only if
                    # Pac-Man can move in that direction
                    if wanted is not None:
                        if self.pacman.can_move(self.maze, wanted):
                            self.pacman.direction = wanted
                            self.requested_direction = None

                    if self.pacman.can_move(self.maze, self.pacman.direction):
                        self.pacman.move(self.maze, self.pacman.direction)
                        # Check if Pac-Man has eaten a normal Pac-Gum.
                        if eat_pac_gum(self.pacman.position, self.pac_gums):
                            self.score += self.points_per_pacgum
                        # Check whether Pac-Man has eaten a Super Pac-Gum.
                        elif eat_pac_gum(self.pacman.position,
                                         self.super_pac_gums):
                            self.score += self.points_per_super_pacgum
                            self.frightened_active = True
                            self.frightened_timer = self.FRIGHTENED_DURATION
                            for ghost in self.ghosts:
                                ghost.set_frightened()

                self.pacman.update(dt) # pacman animation
                # Level won True if no more pac_gums to eat
                self.level_won = not self.pac_gums
                
                # ===================== Drawing MAZE, PAC_MAN, GHOST, GUMS ===============
                self.screen.fill(draw.BLACK)
                draw.draw_maze(self.screen, self.maze, self.cell_size)
                draw_pac_gums(self.screen, self.pac_gums, self.cell_size)
                draw_super_pac_gums(self.screen, self.super_pac_gums,
                                    self.cell_size)
                self.pacman.draw(self.screen)
                for ghost in self.ghosts:
                    ghost.draw(self.screen)

                # ============================ Time Management for pause mode ============================
                now = time.monotonic()
                if self.pause_start is not None:
                    self.paused_time += now - self.pause_start
                    self.pause_start = None
                elapsed_time = (now - self.start_time - self.paused_time) * 1000
                if elapsed_time >= self.level_max_time:
                    self.running = False
                    draw.draw_time_finish(self.screen)
                    pygame.display.flip()
                    end = time.monotonic() + 1.5
                    while time.monotonic() < end:
                        self.clock.tick(self.FPS)
                remaining_time = max(0, int((self.level_max_time - elapsed_time) // 1000))
                y_top = len(self.maze) * self.cell_size
                draw.draw_game_info(self.screen, self.score, self.lives,
                              self.level_index + 1, self.cell_size, self.cheat_mode,
                              self.invincibility, remaining_time, y_top)

        # ===== SECOND BIG PART = PAUSED  object are not more update ============================
            if self.paused:
                if self.pause_start is None:
                    self.pause_start = time.monotonic()
                draw.draw_pause(self.screen)

            # =============== Lives Lost ==============================
            if self.life_lost:
                self.pacman.draw(self.screen)
                for ghost in self.ghosts:
                    ghost.draw(self.screen)
                draw.draw_life_lost(self.screen)
                pygame.display.flip()
                end = time.monotonic() + 1.5
                while time.monotonic() < end:
                    self.clock.tick(self.FPS)
                self.life_lost = False
                self.pacman.position = self.pacman.start_position
                for ghost in self.ghosts:
                    ghost.position = ghost.start_position
            
            # =========== Level Won Management ===========================
            if self.level_won:
                draw.draw_level_won(self.screen)
                pygame.display.flip()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        # Close the game if the window is closed.
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        # SPACE starts the next level.
                        if (event.type == pygame.KEYDOWN
                                and event.key == pygame.K_SPACE):
                            self._next_level()
                            waiting = False
                    self.clock.tick(self.FPS)
            # Display the completed frame on the screen.
            pygame.display.flip() 

        return self.score

    def _draw_during_pause(self, time, y_top) -> None:
        """Print info update during pause in cheat_mode."""
        pygame.draw.rect(self.screen, draw.BLACK, (0, y_top, self.screen.get_width(), self.cell_size * 6))
        draw.draw_game_info(self.screen, self.score, self.lives,
                            self.level_index + 1, self.cell_size, self.cheat_mode,
                            self.invincibility, time, y_top)
