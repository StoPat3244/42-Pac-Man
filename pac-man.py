import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # no sms hello from pygame
import sys  # noqa: E402


def main() -> None:
    """This is the main function"""

    if len(sys.argv) > 2:
        print("Please run game as 'python3 pac-man.py config.json'")
        sys.exit(1)

    config_path = sys.argv[1] if len(sys.argv) == 2 else "config.json"

    try:
        import pygame
        from mazegenerator import MazeGenerator  # noqa: F401 type:
        # ignore[import-not-found]
        from start_game import Game  # noqa: E402
        from game_menu import main_menu, game_over  # noqa: E402
        from configuration import Configuration  # noqa: E402
        config = Configuration.build_config(config_path)
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
        print("[ERROR] The necessary modules are not installed.\n"
              "Install it with: make install \n")
        sys.exit()
    except KeyboardInterrupt:
        print("[INFO] Program terminated by the user.")
    except Exception as e:
        print("[ERROR] ", e)
        sys.exit()
    finally:
        pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[INFO] Program terminated by the user.")
        sys.exit(130)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
