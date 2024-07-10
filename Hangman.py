import pygame
import random
import string

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FONT_SIZE = 36
BUTTON_FONT_SIZE = 28
CATEGORY_FONT_SIZE = 24
BUTTON_PADDING = 10
FPS = 30

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman")

# Set up the fonts
font = pygame.font.Font(None, FONT_SIZE)
button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)
category_font = pygame.font.Font(None, CATEGORY_FONT_SIZE)

# Function to read words and categories from words.txt
def read_words_from_file(file_path):
    categories = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        category = None
        for line in lines:
            line = line.strip()
            if line.startswith("##"):
                category = line[3:].strip()
                categories[category] = []
            elif line and category:
                categories[category].append(line)
    return categories

# Load words and categories
categories = read_words_from_file("words.txt")

# Function to reset the game
def reset_game(category):
    global chosen_word, display, lives, guessed_letters, buttons, category_name, hangman_alpha
    category_name = category
    chosen_word = random.choice(categories[category])
    display = ["_"] * len(chosen_word)
    lives = 6
    guessed_letters = []
    buttons = create_buttons()
    hangman_alpha = 255  # Initialize transparency for fade-in animation

# Function to create buttons for letters
def create_buttons():
    buttons = []
    alphabet = string.ascii_lowercase
    button_width = 40
    button_height = 40
    for i, letter in enumerate(alphabet):
        x = BUTTON_PADDING + (i % 13) * (button_width + BUTTON_PADDING)
        y = HEIGHT - 2 * button_height - 100 + (i // 13) * (button_height + BUTTON_PADDING)
        button_rect = pygame.Rect(x, y, button_width, button_height)
        buttons.append((letter, button_rect))
    return buttons

# Function to draw buttons on the screen
def draw_buttons(buttons):
    for letter, button_rect in buttons:
        color = GRAY if letter in guessed_letters else BLACK
        pygame.draw.rect(screen, color, button_rect)
        text = button_font.render(letter.upper(), True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)

# Function to check if a button is clicked
def check_button_click(pos, buttons):
    for letter, button_rect in buttons:
        if button_rect.collidepoint(pos):
            return letter
    return None

# Function to draw the screen
def draw_screen():
    screen.fill(WHITE)
    # Fade-in animation for the hangman image
    hangman_image = hangman_images[6 - lives].copy()  # Adjust image index based on lives
    hangman_image.set_alpha(hangman_alpha)
    screen.blit(hangman_image, (WIDTH // 2 - 100, 50))
    text = font.render(" ".join(display), True, BLACK)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
    text = font.render(f"Lives: {lives}", True, BLACK)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))
    category_text = category_font.render(f"Category: {category_name}", True, BLACK)
    screen.blit(category_text, (10, 10))
    draw_buttons(buttons)

    # Draw sparkles
    for sparkle in sparkles:
        pygame.draw.circle(screen, sparkle["color"], (sparkle["x"], sparkle["y"]), sparkle["size"])

    pygame.display.flip()

# Function to draw the end message
def draw_end_message(message):
    text = font.render(message, True, RED)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 + 100))
    pygame.display.flip()
    pygame.time.wait(2000)

# Load hangman images in the correct order
hangman_images = [pygame.image.load(f"hangman{i}.jpg") for i in range(7)]

# Initialize sparkles list
sparkles = []

# Function to create sparkle effect
def create_sparkle(x, y):
    sparkle = {
        "x": x,
        "y": y,
        "size": random.randint(5, 15),
        "color": random.choice([WHITE, GRAY, GREEN, RED])  # Customize colors as needed
    }
    return sparkle

# Main game loop
running = True
choosing_category = True
clock = pygame.time.Clock()

while running:
    if choosing_category:
        screen.fill(WHITE)
        category_text = category_font.render("Choose a category:", True, BLACK)
        screen.blit(category_text, (WIDTH // 2 - 100, HEIGHT // 2 - 200))
        category_buttons = []
        for i, category in enumerate(categories.keys()):
            button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 150 + i * 50, 200, 40)
            pygame.draw.rect(screen, BLACK, button_rect)
            text = button_font.render(category, True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
            category_buttons.append((category, button_rect))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                choosing_category = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for category, button_rect in category_buttons:
                    if button_rect.collidepoint(pos):
                        reset_game(category)
                        choosing_category = False
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                letter = check_button_click(pos, buttons)
                if letter and letter not in guessed_letters:
                    guessed_letters.append(letter)
                    if letter in chosen_word:
                        for i in range(len(chosen_word)):
                            if chosen_word[i] == letter:
                                display[i] = letter
                        # Create sparkles at mouse position
                        sparkles.append(create_sparkle(pos[0], pos[1]))
                    else:
                        lives -= 1

        # Update sparkles position and size
        for sparkle in sparkles:
            sparkle["size"] -= 1  # Decrease size over time
            if sparkle["size"] <= 0:
                sparkles.remove(sparkle)

        draw_screen()

        if "_" not in display:
            draw_end_message("You win!")
            choosing_category = True
        elif lives == 0:
            draw_end_message(f"You lose. The word was {chosen_word}")
            choosing_category = True

        clock.tick(FPS)

pygame.quit()
