"""
Flappy Bird Game Implementation
A game where players control a bird that must fly between pipes without hitting them.
"""

import sys
import os
import random
import pygame
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, BLACK, BLUE, GREEN, RED, YELLOW, ORANGE,
    PIPE_WIDTH, PIPE_GAP, PIPE_FREQUENCY,
    GRAVITY, FLAP_STRENGTH, BIRD_WIDTH, BIRD_HEIGHT
)
from utils import draw_text, Button, create_shadow_text, draw_rounded_rect
from leaderboard import add_score, get_high_score

class Bird:
    def __init__(self, theme):
        """Initialize the bird"""
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT // 2,
            BIRD_WIDTH,
            BIRD_HEIGHT
        )
        self.color = theme['player']
        self.velocity = 0
        self.theme = theme
        self.angle = 0  # For rotation effect
        
    def update(self):
        """Update bird position"""
        # Apply gravity
        self.velocity += GRAVITY
        self.rect.y += self.velocity
        
        # Update rotation based on velocity
        self.angle = -self.velocity * 3
        self.angle = max(-30, min(self.angle, 30))  # Limit rotation angle
        
        # Keep bird on screen
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0
            
        if self.rect.bottom > SCREEN_HEIGHT - 50:  # ground level
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.velocity = 0
            
    def flap(self):
        """Make the bird flap (jump)"""
        self.velocity = FLAP_STRENGTH
        
    def draw(self, surface):
        """Draw the bird"""
        # Create a rotated bird surface
        bird_surface = pygame.Surface((BIRD_WIDTH, BIRD_HEIGHT), pygame.SRCALPHA)
        
        # Draw bird body (oval shape)
        pygame.draw.ellipse(bird_surface, self.color, (0, 0, BIRD_WIDTH, BIRD_HEIGHT))
        
        # Add eye
        pygame.draw.circle(
            bird_surface,
            WHITE,
            (BIRD_WIDTH - 8, BIRD_HEIGHT // 3),
            3
        )
        pygame.draw.circle(
            bird_surface,
            BLACK,
            (BIRD_WIDTH - 7, BIRD_HEIGHT // 3),
            1
        )
        
        # Add beak
        pygame.draw.polygon(
            bird_surface,
            ORANGE,
            [
                (BIRD_WIDTH, BIRD_HEIGHT // 2),
                (BIRD_WIDTH + 8, BIRD_HEIGHT // 2 - 2),
                (BIRD_WIDTH + 8, BIRD_HEIGHT // 2 + 2)
            ]
        )
        
        # Add wing
        pygame.draw.ellipse(
            bird_surface,
            tuple(max(c - 40, 0) for c in self.color),
            (5, BIRD_HEIGHT // 2, BIRD_WIDTH // 2, BIRD_HEIGHT // 2)
        )
        
        # Rotate the bird surface
        rotated_bird = pygame.transform.rotate(bird_surface, self.angle)
        rotated_rect = rotated_bird.get_rect(center=self.rect.center)
        
        # Draw to screen
        surface.blit(rotated_bird, rotated_rect.topleft)

class Pipe:
    def __init__(self, x, theme):
        """Initialize a pair of pipes"""
        self.theme = theme
        self.color = theme['obstacle']
        self.width = PIPE_WIDTH
        self.speed = 3
        self.passed = False  # Track if bird has passed this pipe
        self.gap_y = random.randint(PIPE_GAP, SCREEN_HEIGHT - PIPE_GAP)
        
        # Create pipe rectangles
        self.top_rect = pygame.Rect(
            x,
            0,
            self.width,
            self.gap_y - PIPE_GAP // 2
        )
        
        self.bottom_rect = pygame.Rect(
            x,
            self.gap_y + PIPE_GAP // 2,
            self.width,
            SCREEN_HEIGHT - (self.gap_y + PIPE_GAP // 2)
        )
        
    def update(self):
        """Update pipe position"""
        self.top_rect.x -= self.speed
        self.bottom_rect.x -= self.speed
        
        # Check if pipe is off screen
        return self.top_rect.right < 0
        
    def check_collision(self, bird):
        """Check if bird collides with pipes"""
        return bird.rect.colliderect(self.top_rect) or bird.rect.colliderect(self.bottom_rect)
        
    def draw(self, surface):
        """Draw the pipes"""
        # Top pipe
        pygame.draw.rect(surface, self.color, self.top_rect)
        # Add a cap to the top pipe
        cap_rect = pygame.Rect(
            self.top_rect.x - 5,
            self.top_rect.bottom - 15,
            self.width + 10,
            15
        )
        pygame.draw.rect(surface, self.color, cap_rect)
        pygame.draw.rect(surface, BLACK, cap_rect, 1)
        
        # Bottom pipe
        pygame.draw.rect(surface, self.color, self.bottom_rect)
        # Add a cap to the bottom pipe
        cap_rect = pygame.Rect(
            self.bottom_rect.x - 5,
            self.bottom_rect.top,
            self.width + 10,
            15
        )
        pygame.draw.rect(surface, self.color, cap_rect)
        pygame.draw.rect(surface, BLACK, cap_rect, 1)
        
        # Add some detail (pipe segments)
        for pipe_rect in [self.top_rect, self.bottom_rect]:
            for i in range(1, pipe_rect.height // 30):
                y = pipe_rect.top + i * 30
                pygame.draw.line(
                    surface,
                    BLACK,
                    (pipe_rect.left, y),
                    (pipe_rect.right, y),
                    1
                )

class Ground:
    def __init__(self, theme):
        """Initialize the ground"""
        self.theme = theme
        self.rect = pygame.Rect(
            0,
            SCREEN_HEIGHT - 50,
            SCREEN_WIDTH,
            50
        )
        self.color = theme.get('ground', (139, 69, 19))  # Brown if not in theme
        self.scroll = 0
        self.scroll_speed = 3
        
    def update(self):
        """Update ground scroll position"""
        self.scroll = (self.scroll + self.scroll_speed) % 30
        
    def draw(self, surface):
        """Draw the ground"""
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw ground details (grass tufts or dirt lines)
        for i in range(20):
            x = (i * 30 - self.scroll) % SCREEN_WIDTH
            # Draw a small grass tuft
            pygame.draw.polygon(
                surface,
                GREEN,
                [
                    (x, self.rect.top),
                    (x + 5, self.rect.top - 5),
                    (x + 10, self.rect.top)
                ]
            )
            
        # Draw a line along the top of the ground
        pygame.draw.line(
            surface,
            BLACK,
            (0, self.rect.top),
            (SCREEN_WIDTH, self.rect.top),
            1
        )

class Cloud:
    def __init__(self, theme):
        """Initialize a cloud"""
        self.theme = theme
        self.x = SCREEN_WIDTH + random.randint(0, 100)
        self.y = random.randint(50, SCREEN_HEIGHT // 2)
        self.width = random.randint(60, 120)
        self.height = random.randint(30, 50)
        self.speed = random.uniform(0.5, 1.5)
        
    def update(self):
        """Update cloud position"""
        self.x -= self.speed
        # Check if cloud is off screen
        return self.x + self.width < 0
        
    def draw(self, surface):
        """Draw the cloud"""
        # Draw several overlapping circles for cloud shape
        cloud_color = (240, 240, 250)  # White with slight blue tint
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Draw multiple circles to form cloud shape
        circle_positions = [
            (center_x, center_y),
            (center_x - self.width // 4, center_y),
            (center_x + self.width // 4, center_y),
            (center_x - self.width // 3, center_y - self.height // 4),
            (center_x + self.width // 3, center_y - self.height // 4),
            (center_x, center_y - self.height // 3)
        ]
        
        for pos in circle_positions:
            radius = random.randint(self.height // 2, self.height)
            pygame.draw.circle(surface, cloud_color, pos, radius)

def run_flappy_game(theme):
    """Run the Flappy Bird game"""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()
    
    # Create fonts
    font = pygame.font.SysFont('Arial', 24)
    title_font = pygame.font.SysFont('Arial', 36, bold=True)
    score_font = pygame.font.SysFont('Arial', 32, bold=True)
    
    # Initialize game objects
    bird = Bird(theme)
    pipes = []
    ground = Ground(theme)
    clouds = [Cloud(theme) for _ in range(3)]
    
    # Game states
    game_active = False
    game_over = False
    paused = False
    score = 0
    high_score = get_high_score("Flappy Bird")
    
    # Time tracking for pipe spawning
    last_pipe_time = pygame.time.get_ticks()
    
    # Buttons
    start_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT // 2 + 50,
        200,
        50,
        "Start Game",
        GREEN
    )
    
    restart_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT // 2 + 20,
        200,
        50,
        "Play Again",
        GREEN
    )
    
    menu_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT // 2 + 90,
        200,
        50,
        "Back to Menu",
        BLUE
    )
    
    # Pause button
    pause_button = Button(
        SCREEN_WIDTH - 90,
        10,
        80,
        30,
        "Pause",
        theme['text']
    )
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle key events
            if event.type == pygame.KEYDOWN:
                # Space to flap
                if event.key == pygame.K_SPACE:
                    if game_active and not paused:
                        bird.flap()
                    # Start game with space
                    elif not game_active and not game_over:
                        game_active = True
                    # Restart game with space
                    elif game_over:
                        # Reset game
                        game_active = True
                        game_over = False
                        bird = Bird(theme)
                        pipes = []
                        score = 0
                        last_pipe_time = pygame.time.get_ticks()
                    
                # Pause/unpause
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    if game_active:
                        paused = not paused
                        
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Flap on click
                if game_active and not paused:
                    bird.flap()
                    
                # Start screen buttons
                if not game_active and not game_over:
                    if start_button.is_clicked(mouse_pos):
                        game_active = True
                        
                # Game over screen buttons
                elif game_over:
                    if restart_button.is_clicked(mouse_pos):
                        # Reset game
                        game_active = True
                        game_over = False
                        bird = Bird(theme)
                        pipes = []
                        score = 0
                        last_pipe_time = pygame.time.get_ticks()
                    elif menu_button.is_clicked(mouse_pos):
                        return score
                        
                # Pause button during gameplay
                elif game_active:
                    if pause_button.is_clicked(mouse_pos):
                        paused = not paused
        
        # Fill the screen
        screen.fill(theme.get('sky', (135, 206, 235)))  # Sky blue if not in theme
        
        # Draw clouds
        for cloud in clouds[:]:
            cloud.draw(screen)
            if not paused and game_active:
                if cloud.update():
                    clouds.remove(cloud)
                    clouds.append(Cloud(theme))
                    
        # Start screen
        if not game_active and not game_over:
            # Draw title
            create_shadow_text(
                screen,
                "FLAPPY BIRD",
                title_font,
                theme['text'],
                BLACK,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 4
            )
            
            # Draw bird as mascot
            mascot_bird = Bird(theme)
            mascot_bird.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50)
            mascot_bird.draw(screen)
            
            # Draw instructions
            instructions = [
                "Press SPACE or Click to flap",
                "Avoid the pipes!",
                "Press ESC or P to pause"
            ]
                
            for i, instruction in enumerate(instructions):
                draw_text(
                    screen,
                    instruction,
                    font,
                    theme['text'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 30 + i * 30
                )
                
            # Draw high score
            draw_text(
                screen,
                f"High Score: {high_score}",
                score_font,
                theme['accent1'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 90
            )
                
            # Draw start button
            start_button.draw(screen, theme)
            
        # Game over screen
        elif game_over:
            # Draw game over text
            create_shadow_text(
                screen,
                "GAME OVER",
                title_font,
                RED,
                BLACK,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 3
            )
            
            # Draw score
            draw_text(
                screen,
                f"Score: {score}",
                score_font,
                theme['text'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 50
            )
            
            # Draw high score
            if score > high_score:
                draw_text(
                    screen,
                    "NEW HIGH SCORE!",
                    score_font,
                    theme['accent1'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2
                )
                high_score = score
            else:
                draw_text(
                    screen,
                    f"High Score: {high_score}",
                    score_font,
                    theme['accent1'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2
                )
                
            # Draw buttons
            restart_button.draw(screen, theme)
            menu_button.draw(screen, theme)
            
        # Active gameplay
        elif game_active:
            # Update game objects if not paused
            if not paused:
                # Update bird
                bird.update()
                
                # Update ground
                ground.update()
                
                # Check for pipe spawn
                current_time = pygame.time.get_ticks()
                if current_time - last_pipe_time > PIPE_FREQUENCY:
                    pipes.append(Pipe(SCREEN_WIDTH, theme))
                    last_pipe_time = current_time
                    
                # Update pipes
                for pipe in pipes[:]:
                    if pipe.update():
                        pipes.remove(pipe)
                        
                    # Check if bird passed pipe
                    if not pipe.passed and pipe.top_rect.right < bird.rect.left:
                        pipe.passed = True
                        score += 1
                        
                    # Check for collision
                    if pipe.check_collision(bird):
                        game_active = False
                        game_over = True
                        
                        # Update high score
                        if score > high_score:
                            add_score("Flappy Bird", score)
                            
                # Check for ground collision
                if bird.rect.bottom >= ground.rect.top:
                    game_active = False
                    game_over = True
                    
                    # Update high score
                    if score > high_score:
                        add_score("Flappy Bird", score)
            
            # Draw pipes
            for pipe in pipes:
                pipe.draw(screen)
                
            # Draw ground
            ground.draw(screen)
            
            # Draw bird
            bird.draw(screen)
            
            # Draw score
            create_shadow_text(
                screen,
                str(score),
                score_font,
                WHITE,
                BLACK,
                SCREEN_WIDTH // 2,
                50
            )
            
            # Draw pause button
            pause_button.draw(screen, theme)
            
            # If paused, draw pause overlay
            if paused:
                # Semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                
                # Pause text
                draw_text(
                    screen,
                    "PAUSED",
                    title_font,
                    WHITE,
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 50
                )
                
                # Resume instructions
                draw_text(
                    screen,
                    "Press ESC or P to Resume",
                    font,
                    WHITE,
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2
                )
                
                # Menu option
                draw_text(
                    screen,
                    "Press BACKSPACE to Return to Menu",
                    font,
                    WHITE,
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 40
                )
                
                # Check for menu return
                keys = pygame.key.get_pressed()
                if keys[pygame.K_BACKSPACE]:
                    return score
        
        # Draw ground even on start/game over screens
        if not game_active or game_over:
            ground.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    return score

if __name__ == "__main__":
    # For testing the game standalone
    from themes import DEFAULT_THEMES
    run_flappy_game(DEFAULT_THEMES["Classic"])
