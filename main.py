import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1250
SCREEN_HEIGHT = 900
BRICK_WIDTH = 115
BRICK_HEIGHT = 26
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
BALL_RADIUS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Breakout Game")

# Define all_sprites globally
all_sprites = pygame.sprite.Group()

# Paddle class
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PADDLE_WIDTH, PADDLE_HEIGHT])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = (SCREEN_WIDTH - PADDLE_WIDTH) // 2
        self.rect.y = SCREEN_HEIGHT - 40
        self.original_width = PADDLE_WIDTH

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0] - self.rect.width // 2
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width

    def resize(self, width):
        self.rect.width = width
        self.image = pygame.Surface([self.rect.width, PADDLE_HEIGHT])
        self.image.fill(WHITE)

    def reset_size(self):
        self.resize(self.original_width)

# Ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([BALL_RADIUS * 2, BALL_RADIUS * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - BALL_RADIUS
        self.rect.y = SCREEN_HEIGHT // 2 - BALL_RADIUS
        self.dx = random.choice([-4, 4])
        self.dy = -4
        self.size_multiplier = 1
        self.golden = False

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.x <= 0 or self.rect.x >= SCREEN_WIDTH - BALL_RADIUS * 2 * self.size_multiplier:
            self.dx *= -1
        if self.rect.y <= 0:
            self.dy *= -1
        if self.rect.y >= SCREEN_HEIGHT:
            self.kill()
            show_game_over_screen()

        # Check for collision with the paddle
        if pygame.sprite.collide_rect(self, paddle):
            self.dy *= -1
            self.rect.y = paddle.rect.y - BALL_RADIUS * 2 * self.size_multiplier

        # Check for collision with bricks if not golden
        if not self.golden:
            brick_collision_list = pygame.sprite.spritecollide(self, bricks, True)
            if brick_collision_list:
                self.dy *= -1
                global score
                score += 1
                spawn_power_ups(brick_collision_list[0].rect)
                if len(bricks) == 0:
                    reset_bricks()

    def resize(self, multiplier):
        self.size_multiplier = multiplier
        new_radius = BALL_RADIUS * multiplier
        self.image = pygame.Surface([new_radius * 2, new_radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (new_radius, new_radius), new_radius)
        self.rect = self.image.get_rect()

    def set_golden(self, golden):
        self.golden = golden
        if golden:
            self.image.fill(YELLOW)
        else:
            self.image.fill(WHITE)

# Brick class
class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([BRICK_WIDTH, BRICK_HEIGHT])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power):
        super().__init__()
        self.power = power
        self.image = pygame.Surface([50, 20])
        self.color = GREEN if power in ["Bigger", "BiggerBall", "GoldenBall"] else RED
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.font = pygame.font.Font(None, 24)
        self.text = self.font.render(power, True, BLACK)
        self.image.blit(self.text, (5, 2))

    def update(self):
        self.rect.y += 2
        if self.rect.y >= SCREEN_HEIGHT:
            self.kill()

# Function to show the game over screen
def show_game_over_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)

    text = font.render("GAME OVER", 1, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

    # Draw restart button
    restart_font = pygame.font.Font(None, 50)
    restart_text = restart_font.render("RESTART", 1, BLACK)
    restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
    restart_game = False

    while not restart_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    restart_game = True

        # Change button color on hover
        mouse_pos = pygame.mouse.get_pos()
        if restart_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, YELLOW, restart_rect)
        else:
            pygame.draw.rect(screen, WHITE, restart_rect)

        screen.blit(restart_text, (restart_rect.x + (restart_rect.width - restart_text.get_width()) // 2, restart_rect.y + (restart_rect.height - restart_text.get_height()) // 2))
        pygame.display.flip()

    # Restart the game
    main()

# Function to show the start screen with a "Start" button
def show_start_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    title_text = font.render("BREAKOUT", 1, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - title_text.get_height() // 2 - 100))

    button_font = pygame.font.Font(None, 50)
    button_text = button_font.render("START", 1, BLACK)
    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50)
    start_game = False

    while not start_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    start_game = True

        # Change button color on hover
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, YELLOW, button_rect)
        else:
            pygame.draw.rect(screen, WHITE, button_rect)

        screen.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width()) // 2, button_rect.y + (button_rect.height - button_text.get_height()) // 2))
        pygame.display.flip()

# Function to create bricks with spacing
def create_bricks():
    bricks = pygame.sprite.Group()
    for row in range(5):
        for col in range(10):
            if random.random() > 0.2:  # 20% chance to leave a space
                brick = Brick(col * (BRICK_WIDTH + 5) + 35, row * (BRICK_HEIGHT + 5) + 35)
                all_sprites.add(brick)
                bricks.add(brick)
    return bricks

# Function to spawn power-ups and power-downs
def spawn_power_ups(brick_rect):
    power_ups = pygame.sprite.Group()
    powers = ["Bigger", "BiggerBall", "FasterBall", "Smaller"]
    for _ in range(random.randint(0, 2)):  # Randomly drop 0, 1, or 2 power-ups/downs
        power = random.choice(powers)
        power_up = PowerUp(brick_rect.x + brick_rect.width // 2 - 25, brick_rect.y + brick_rect.height // 2 - 10, power)
        all_sprites.add(power_up)
        power_ups.add(power_up)


# Function to reset bricks
def reset_bricks():
    global bricks
    bricks = create_bricks()

# Main game loop
def main():
    global paddle, ball, bricks, score, all_sprites, bigger_ball_timer

    all_sprites = pygame.sprite.Group()
    score = 0
    bigger_ball_timer = 0  # Initialize bigger ball timer

    # Create paddle
    paddle = Paddle()
    all_sprites.add(paddle)

    # Create ball
    ball = Ball()
    all_sprites.add(ball)

    # Create bricks
    bricks = create_bricks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update paddle, ball, and power-ups
        all_sprites.update()

        # Update bigger ball timer
        if bigger_ball_timer > 0:
            bigger_ball_timer -= 1
            if bigger_ball_timer == 0:
                ball.resize(1)  # Reset ball size when timer expires

        # Check for power-up collision with paddle
        power_up_collisions = pygame.sprite.spritecollide(paddle, all_sprites, False)
        for power_up in power_up_collisions:
            if isinstance(power_up, PowerUp):
                power_up.kill()
                if power_up.power == "Bigger":
                    paddle.resize(PADDLE_WIDTH * 1.5)
                elif power_up.power == "BiggerBall":
                    ball.resize(3)
                    bigger_ball_timer = 600  # Set timer to 10 seconds (60 frames per second * 10 seconds)
                elif power_up.power == "GoldenBall":
                    ball.set_golden(True)
                elif power_up.power == "FasterBall":
                    ball.dx *= 1.5
                    ball.dy *= 1.5
                elif power_up.power == "Smaller":
                    paddle.resize(PADDLE_WIDTH * 0.5)

        # Clear the screen
        screen.fill(BLACK)

        # Draw all sprites
        all_sprites.draw(screen)

        # Draw the score
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {score}", 1, WHITE)
        screen.blit(text, (10, 10))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        pygame.time.Clock().tick(60)

# Show start screen
show_start_screen()

# Start the main game loop
main()
