import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship Wars")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Starfield class to handle the background stars
class Starfield:
    def __init__(self, num_stars):
        self.stars = []
        for _ in range(num_stars):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            speed = random.randint(1, 3)  # Vary the speed of the stars
            self.stars.append([x, y, speed])

    def move_stars(self):
        for star in self.stars:
            star[1] += star[2]  # Move the star downwards by its speed
            if star[1] > HEIGHT:  # Reset star to the top if it goes off the screen
                star[1] = 0
                star[0] = random.randint(0, WIDTH)  # Random horizontal position

    def draw(self):
        for star in self.stars:
            pygame.draw.circle(screen, WHITE, (star[0], star[1]), 2)

# Load spaceship images and remove white background
ship1_image = pygame.image.load("SPACESHIP.png")
ship2_image = pygame.image.load("SPACESHIP.png")

# Remove the white background (make it transparent)
ship1_image.set_colorkey((255, 255, 255))  # Remove white background from ship1
ship2_image.set_colorkey((255, 255, 255))  # Remove white background from ship2

# Resize the images
ship1_image = pygame.transform.scale(ship1_image, (50, 50))
ship2_image = pygame.transform.scale(ship2_image, (50, 50))

# Font setup
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Bullet class for trajectory motion
class Bullet:
    def __init__(self, x, y, angle, speed):
        self.x = x
        self.y = y
        self.angle = math.radians(angle)
        self.speed = speed
        self.time = 0

    def move(self):
        self.time += 0.1
        gravity = 0.5
        # Update bullet's x and y using projectile motion equations
        self.x += self.speed * math.cos(self.angle)
        self.y -= (self.speed * math.sin(self.angle) - gravity * self.time ** 2)

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 5)

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y > HEIGHT

# Ship class
class Spaceship:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.bullets = []
        self.alive = True
        self.health = 100  # Initialize with 100 health points

    def draw(self):
        if self.alive:
            screen.blit(self.image, (self.x, self.y))
            self.draw_health_bar()  # Draw health bar above the spaceship
        for bullet in self.bullets:
            bullet.draw()

    def draw_health_bar(self):
        # Draw a red background bar
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, 50, 5))
        # Draw a green foreground bar proportional to the health
        health_width = int(50 * (self.health / 100))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_width, 5))

    def move_bullets(self, opponent):
        for bullet in self.bullets[:]:
            bullet.move()
            if self.check_collision(bullet, opponent):
                opponent.health -= 20  # Decrease opponent's health by 20 on collision
                if opponent.health <= 0:
                    opponent.alive = False  # Mark as dead only when health reaches 0
                self.bullets.remove(bullet)
            elif bullet.off_screen() and bullet.y > 0:
                bullet.time = 0
            elif bullet.off_screen() and bullet.y <= 0:
                self.bullets.remove(bullet)

    def check_collision(self, bullet, opponent):
        if (opponent.x < bullet.x < opponent.x + 50) and (opponent.y < bullet.y < opponent.y + 50):
            return True
        return False

# Player setup
def reset_game():
    global player1, player2, game_over, winner, starfield
    player1 = Spaceship(100, HEIGHT // 2, ship1_image)
    player2 = Spaceship(WIDTH - 150, HEIGHT // 2, ship2_image)
    game_over = False
    winner = None
    starfield = Starfield(num_stars=200)  # Initialize starfield with 200 stars

reset_game()

# Game loop control
running = True
clock = pygame.time.Clock()

# Main game loop
while running:
    screen.fill(BLACK)  # Fill screen with black before drawing background

    # Move and draw the starfield background
    starfield.move_stars()
    starfield.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Restart the game if 'R' is pressed
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                reset_game()

            # Shooting bullets
            if not game_over:
                if event.key == pygame.K_SPACE and player1.alive:  # Player 1 shoot
                    # Random angle between 30 to 60 degrees
                    angle = random.randint(30, 60)
                    bullet = Bullet(player1.x + 50, player1.y + 25, angle=angle, speed=10)
                    player1.bullets.append(bullet)
                if event.key == pygame.K_RETURN and player2.alive:  # Player 2 shoot
                    # Random angle between 120 to 150 degrees
                    angle = random.randint(120, 150)
                    bullet = Bullet(player2.x, player2.y + 25, angle=angle, speed=10)
                    player2.bullets.append(bullet)

    # Check if the game is over
    if player1.health <= 0 or player2.health <= 0:
        game_over = True
        winner = "Player 2" if player1.health <= 0 else "Player 1"

    if game_over:
        # Display GAME OVER and the winner
        game_over_text = font.render("GAME OVER", True, WHITE)
        winner_text = small_font.render(f"{winner} Wins!", True, GREEN)
        restart_text = small_font.render("Press R to Restart", True, WHITE)

        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
    else:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player1.y > 0:
            player1.y -= 5
        if keys[pygame.K_s] and player1.y < HEIGHT - 50:
            player1.y += 5
        if keys[pygame.K_UP] and player2.y > 0:
            player2.y -= 5
        if keys[pygame.K_DOWN] and player2.y < HEIGHT - 50:
            player2.y += 5

        # Move and draw bullets
        player1.move_bullets(player2)
        player2.move_bullets(player1)

        # Draw players
        player1.draw()
        player2.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
