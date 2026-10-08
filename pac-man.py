import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # no sms hello from pygame
import pygame  # noqa: E402
import sys  # noqa: E402
from start_game import Game  # noqa: E402
from game_menu import main_menu, game_over  # noqa: E402
from configuration import Configuration  # noqa: E402


def main() -> None:
    """This is the main function"""

    if len(sys.argv) != 2:
        print("Please run game as 'python3 pac-man.py config.json'")
        sys.exit(1)

    try:
        from mazegenerator import MazeGenerator  # noqa: F401
        config = Configuration.build_config(sys.argv[1])
        pygame.init()
        info = pygame.display.Info()
        WIDTH = info.current_w
        HEIGHT = info.current_h
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Pac-Man")
        running = True
        while running:
            if not main_menu(screen, config):
                pygame.quit()
                return
            score: int
            winner: bool
            score, winner = Game(screen, config).run()
            game_over(screen, config.h_score, score, winner)
    except ModuleNotFoundError:
        print("[ERROR] The 'mazegenerator' module is not installed.\n"
              "Install it with: pip install mazegenerator\n"
              "or copy the 'mazegenerator' folder into the project directory.")
        sys.exit()
    except KeyboardInterrupt:
        print("[INFO] Program terminated by the user.")
    except Exception as e:
        print("[ERROR] ", e)
        sys.exit()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
