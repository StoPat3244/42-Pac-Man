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

    # Define the spacing between the different elements of the menu.
    gap_after_image = 100
    gap_after_title = 15
    gap_after_instruction = 30
    gap_after_highscore_title = 10
    gap_between_entries = 3

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

        # Get the current screen dimensions to center the menu.
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Render the text elements that will be displayed on the screen.
        title_text = title_font.render("Pac-Man", True, (255, 255, 0))
        instruction_text = instruction_font.render("Push SPACE to play", True, (255, 255, 255))
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

        # Draw the "Highscores" title.
        highscore_title_rect = highscore_title_text.get_rect(center=(center_x, 335))
        screen.blit(highscore_title_text, highscore_title_rect)

        # Draw each highscore entry one below the other.
        current_y = 365
        for text in highscore_entry_texts:
            entry_rect = text.get_rect(center=(center_x, current_y))
            screen.blit(text, entry_rect)
            current_y += text.get_height() + gap_between_entries

        # Update the display so all the drawn elements become visible.
        pygame.display.flip()

    # Return True when the player presses SPACE and wants to start the game.
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


def game_over(score=200):
    pygame.init()

    # Set up the game over window.
    WIDTH, HEIGHT = 600, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
    input_rect = pygame.Rect(150, 250, 300, 45)
    active = True
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
        title_rect = title_text.get_rect(center=(WIDTH // 2, 60))
        screen.blit(title_text, title_rect)

        # Display the player's final score.
        score_text = font.render(f"Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, 130))
        screen.blit(score_text, score_rect)

        # Display instructions for entering the player's name.
        line1 = font.render("Insert your name", True, WHITE)
        line2 = font.render("(Alphanumeric characters only)", True, WHITE)
        rect1 = line1.get_rect(center=(WIDTH // 2, 180))
        rect2 = line2.get_rect(center=(WIDTH // 2, 210))

        screen.blit(line1, rect1)
        screen.blit(line2, rect2)

        # Draw the input box around the name field.
        pygame.draw.rect(
            screen,
            BLUE if active else GRAY,
            input_rect,
            2
        )

        # Display the name currently entered by the player.
        name_text = font.render(name, True, WHITE)
        name_x = input_rect.x + 10
        name_y = input_rect.y + 8
        screen.blit(name_text, (name_x, name_y))

        # Draw the blinking cursor after the last character.
        if active and cursor_visible:
            cursor_x = name_x + name_text.get_width() + 2
            cursor_y = name_y
            cursor_height = name_text.get_height()
            pygame.draw.rect(
                screen,
                WHITE,
                (cursor_x, cursor_y, 2, cursor_height)
            )

        # Update the display and limit the loop to 60 frames per second.
        pygame.display.flip()
        clock.tick(60)

    # Close Pygame when the game over screen is finished.
    pygame.quit()
