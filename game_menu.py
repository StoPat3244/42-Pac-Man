import pygame
import json
import os
from pathlib import Path


MAX_NAME_LENGTH = 20


def load_highscores(filename: str = "data/score.json") -> list[dict]:
    # Define the maximum number of highscores to display.
    MAX_HIGHSCORES_DISPLAYED = 10
    # Build the path to the score file relative to this Python file.
    BASE_DIR = Path(__file__).resolve().parent
    filename = BASE_DIR / "data" / "score.json"
    # Check if the score file exists before trying to open it.
    if not os.path.isfile(filename):
        print("The path of the 'score file' is incorrect")
        return []
    try:
        # Load the JSON file and convert its contents into Python objects.
        with open(filename, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        # Return an empty list if the file cannot be read or contains invalid JSON.
        return []
    # The JSON data must be a list containing the highscore entries.
    if not isinstance(data, list):
        return []
    valid_entries = []
    # Check each entry and keep only valid players and scores.
    for entry in data:
        if not isinstance(entry, dict):
            continue
        # Only accept entries with the expected structure.
        if set(entry.keys()) != {"name", "score"}:
            continue
        name = entry["name"]
        score = entry["score"]
        # Make sure the name and score have the correct types and values.
        if not isinstance(name, str):
            continue
        if not isinstance(score, int) or isinstance(score, bool) or score < 0:
            continue
        # Store the valid entry, limiting the player's name to 10 characters.
        valid_entries.append({
            "name": name[:MAX_NAME_LENGTH],
            "score": score
        })
    # Sort all valid scores from highest to lowest.
    valid_entries.sort(key=lambda entry: entry["score"], reverse=True)
    # Return only the 10 highest scores.
    return valid_entries[:MAX_HIGHSCORES_DISPLAYED]

def main_menu(screen) -> bool:
    # Load and resize the Pac-Man image used in the menu.
    pacman_image = pygame.image.load("pacman.png").convert_alpha()
    pacman_image = pygame.transform.scale(pacman_image, (200, 200))

    # Create the fonts used for the different menu elements.
    title_font = pygame.font.Font(None, 80)
    instruction_font = pygame.font.Font(None, 40)
    highscore_title_font = pygame.font.Font(None, 50)
    highscore_entry_font = pygame.font.Font(None, 32)

    # Load the saved highscores from the score file.
    highscores = load_highscores()

    # Keep displaying the menu until the player starts the game or quits.
    waiting = True
    while waiting:
        # Check for keyboard input and window events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_RETURN:
                    # Open the instructions screen. If the player closes the
                    # window from there, propagate the quit signal upward.
                    if not instructions_screen(screen):
                        return False
                elif event.key == pygame.K_ESCAPE:
                    # Same exit path used for the window close button (QUIT),
                    # so the caller only needs to handle one "stop" signal.
                    return False

        # Get the current screen dimensions to center the menu.
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Render the text elements that will be displayed on the screen.
        title_text = title_font.render("Pac-Man", True, (255, 255, 0))
        instruction_text = instruction_font.render("Push SPACE to play", True, (255, 255, 255))
        instructions_hint_text = instruction_font.render(
            "Push ENTER to read the instructions", True, (255, 255, 255)
        )
        exit_hint_text = instruction_font.render("Push ESC to exit", True, (255, 255, 255))
        highscore_title_text = highscore_title_font.render(
            "Highscores", True, (255, 255, 0)
        )

        # Create one text surface for each player in the highscore list.
        highscore_entry_texts = []
        for rank, entry in enumerate(highscores, start=1):
            line = f"{rank}. {entry['name']} - {entry['score']} pts"
            text = highscore_entry_font.render(line, True, (255, 255, 255))
            highscore_entry_texts.append(text)

        # Clear the screen before drawing the menu again.
        screen.fill((0, 0, 0))

        center_x = screen_width // 2

        # Draw the Pac-Man image at the top of the menu.
        image_rect = pacman_image.get_rect(center=(center_x, 120))
        screen.blit(pacman_image, image_rect)

        # Draw the game title below the image.
        title_rect = title_text.get_rect(center=(center_x, 245))
        screen.blit(title_text, title_rect)

        # Draw the instruction telling the player how to start the game.
        instruction_rect = instruction_text.get_rect(center=(center_x, 285))
        screen.blit(instruction_text, instruction_rect)

        # Draw the hint for opening the instructions screen.
        instructions_hint_rect = instructions_hint_text.get_rect(center=(center_x, 320))
        screen.blit(instructions_hint_text, instructions_hint_rect)

        # Draw the hint for exiting the game.
        exit_hint_rect = exit_hint_text.get_rect(center=(center_x, 355))
        screen.blit(exit_hint_text, exit_hint_rect)

        # Draw the "Highscores" title (shifted down to make room for the new hints).
        highscore_title_rect = highscore_title_text.get_rect(center=(center_x, 405))
        screen.blit(highscore_title_text, highscore_title_rect)

        # Draw each highscore entry one below the other.
        current_y = 435
        for text in highscore_entry_texts:
            entry_rect = text.get_rect(center=(center_x, current_y))
            screen.blit(text, entry_rect)
            current_y += text.get_height() + 3

        # Update the display so all the drawn elements become visible.
        pygame.display.flip()

    # Return True when the player presses SPACE and wants to start the game.
    return True


def instructions_screen(screen) -> bool:
    """
    Show the controls and a short explanation of how Pac-Man works.
    Returns True when the player wants to go back to the main menu,
    and False if the window is closed from here (propagated to main_menu).
    """
    title_font = pygame.font.Font(None, 60)
    text_font = pygame.font.Font(None, 32)
    back_font = pygame.font.Font(None, 36)

    # Lines describing controls and rules. An empty string adds extra spacing.
    lines = [
        "Use the ARROW KEYS to move Pac-Man:",
        "UP - move up",
        "DOWN - move down",
        "LEFT - move left",
        "RIGHT - move right",
        "",
        "Eat all the dots scattered around the maze.",
        "Avoid the ghosts: if one touches you, you lose a life.",
        "Eat every dot in the maze to win the level!",
    ]

    waiting = True
    while waiting:
        # Check for keyboard input and window events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

        screen_width = screen.get_width()
        center_x = screen_width // 2

        # Clear the screen before drawing the instructions again.
        screen.fill((0, 0, 0))

        # Draw the screen title.
        title_text = title_font.render("Instructions", True, (255, 255, 0))
        title_rect = title_text.get_rect(center=(center_x, 90))
        screen.blit(title_text, title_rect)

        # Draw each line of the instructions, one below the other.
        current_y = 170
        for line in lines:
            if line == "":
                current_y += 20
                continue
            line_text = text_font.render(line, True, (255, 255, 255))
            line_rect = line_text.get_rect(center=(center_x, current_y))
            screen.blit(line_text, line_rect)
            current_y += line_text.get_height() + 8

        # Draw the hint to go back to the main menu.
        back_text = back_font.render(
            "Push ENTER to come back to the main menu", True, (255, 255, 0)
        )
        back_rect = back_text.get_rect(center=(center_x, current_y + 40))
        screen.blit(back_text, back_rect)

        # Update the display so all the drawn elements become visible.
        pygame.display.flip()

    return True


def save_score(name, score):
    filename = "data/score.json"
    # Load the existing scores if the file is available.
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                scores = json.load(file)

            # Make sure the JSON contains a list of scores.
            if not isinstance(scores, list):
                scores = []
        except (json.JSONDecodeError, FileNotFoundError):
            # Start with an empty list if the file cannot be read correctly.
            scores = []
    else:
        # Create a new empty list if the score file does not exist.
        scores = []
    # Add the new player's score to the existing scores.
    scores.append({
        "name": name,
        "score": score
    })
    # Save all scores back to the JSON file.
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(scores, file, indent=4, ensure_ascii=False)


def game_over(screen, score) -> None:
    restart = False
    pygame.display.set_caption("game over")

    # Create the fonts used in the screen.
    title_font = pygame.font.Font(None, 60)
    font = pygame.font.Font(None, 36)

    # Define the colors used in the interface.
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (180, 180, 180)
    BLUE = (70, 120, 255)

    # Store the name entered by the player.
    name = ""

    # Define the position and size of the name input box.
                            # (x, y, width, height)
    #input_rect = pygame.Rect(screen.get_width() // 2, 250, 300, 45)
    clock = pygame.time.Clock()
    running = True

    # Variables used to make the input cursor blink.
    cursor_visible = True
    cursor_timer = 0
    cursor_blink_time = 500  # milliseconds

    # Keep the game over screen open until the player saves the score or quits.
    while running:
        # Handle keyboard and window events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    restart = True
                    # Save the score only if the player entered a name.
                    if name:
                        save_score(name, score)
                    running = False

                elif event.key == pygame.K_BACKSPACE:
                    # Remove the last character from the name.
                    name = name[:-1]

                else:
                    # Accept only alphanumeric characters, spaces, and names
                    # up to the maximum allowed length.
                    if (event.unicode.isalnum() or event.unicode == " ") and len(name) < MAX_NAME_LENGTH:
                        name += event.unicode

        # Update the cursor timer and toggle its visibility every 500 ms.
        cursor_timer += clock.get_time()
        if cursor_timer >= cursor_blink_time:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        # Clear the screen before drawing the new frame.
        screen.fill(BLACK)

        # Display the "GAME OVER" title.
        title_text = title_font.render("GAME OVER", True, WHITE)
        title_rect = title_text.get_rect(center=(screen.get_width()// 2, 60))
        screen.blit(title_text, title_rect)

        # Display the player's final score.
        score_text = font.render(f"Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(screen.get_width() // 2, 130))
        screen.blit(score_text, score_rect)

        # Display instructions for entering the player's name.
        line1 = font.render("Insert your name", True, WHITE)
        line2 = font.render("(Alphanumeric characters only)", True, WHITE)
        rect1 = line1.get_rect(center=(screen.get_width() // 2, 180))
        rect2 = line2.get_rect(center=(screen.get_width() // 2, 210))

        screen.blit(line1, rect1)
        screen.blit(line2, rect2)

        input_rect = pygame.Rect((screen.get_width() // 2) - 150, 250, 300, 45)
        # Draw the input box around the name field.
        pygame.draw.rect(
            screen,  # superficie su cui disegnare
            BLUE,    # colore
            input_rect,     # posizione del rettangolo
            2               # spessore della linea
        )

        # Display the name currently entered by the player.
        name_text = font.render(name, True, WHITE)
        name_rect = name_text.get_rect(center=input_rect.center)

        screen.blit(name_text, name_rect)
        # Draw the blinking cursor after the last character.
        if cursor_visible:
            cursor_x = name_rect.right + 2
            cursor_y = name_rect.top
            cursor_height = name_rect.height
            pygame.draw.rect(
                screen,
                WHITE,
                (cursor_x, cursor_y, 2, cursor_height)
            )
        # return main_menu
        main_menu_text = font.render("Press ENTER to return to the main menu", True, WHITE)
        main_menu_rect = main_menu_text.get_rect(center=(screen.get_width() // 2, 500))
        screen.blit(main_menu_text, main_menu_rect)
        # Update the display and limit the loop to 60 frames per second.
        pygame.display.flip()
        clock.tick(60)
    return
    # Close Pygame when the game over screen is finished.
    #pygame.quit()
    #if restart:
    #    from main import main
    #    main()
