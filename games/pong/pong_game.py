"""
Pong Game Implementation
Classic two-player Pong game where players control paddles to hit a ball back and forth.
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
    WHITE, BLACK, BLUE, GREEN, RED, GRAY,
    PADDLE_WIDTH, PADDLE_HEIGHT, BALL_SIZE,
    PADDLE_SPEED, BALL_SPEED_X, BALL_SPEED_Y
)
from utils import draw_text, Button, center_rect
from leaderboard import add_score, get_high_score

class Paddle:
    def __init__(self, x, y, width, height, theme, is_player_one=True):
        """Initialize paddle"""
        self.rect = pygame.Rect(x, y, width, height)
        self.color = theme['player'] if is_player_one else theme['opponent']
        self.speed = PADDLE_SPEED
        self.is_player_one = is_player_one
        self.score = 0
        self.theme = theme
        
    def update(self, keys=None, ball=None, ai_difficulty=0):
        """Update paddle position based on keys or AI"""
        if keys:
            # Player controls
            if self.is_player_one:
                if keys[pygame.K_w]:
                    self.move_up()
                if keys[pygame.K_s]:
                    self.move_down()
            else:
                if keys[pygame.K_UP]:
                    self.move_up()
                if keys[pygame.K_DOWN]:
                    self.move_down()
        elif ball and not self.is_player_one:
            # AI controls
            # Track the ball with some delay based on difficulty
            # Difficulty 0 (Easy): Slower reactions, makes mistakes
            # Difficulty 1 (Medium): Decent tracking
            # Difficulty 2 (Hard): Nearly perfect tracking
            
            # Calculate ideal paddle y position to track ball
            target_y = ball.rect.centery - self.rect.height / 2
            
            # Apply difficulty modifiers
            if ai_difficulty == 0:  # Easy
                # Add random movement and delay
                target_y += random.randint(-50, 50)
                reaction_speed = 0.3
            elif ai_difficulty == 1:  # Medium
                # Small random movement
                target_y += random.randint(-20, 20)
                reaction_speed = 0.6
            else:  # Hard
                # Almost perfect tracking with tiny randomness
                target_y += random.randint(-5, 5)
                reaction_speed = 0.9
                
            # Move toward target position
            if self.rect.centery < target_y:
                self.rect.y += min(self.speed * reaction_speed, target_y - self.rect.centery)
            elif self.rect.centery > target_y:
                self.rect.y -= min(self.speed * reaction_speed, self.rect.centery - target_y)
                
            # Keep in bounds
            self.keep_in_bounds()
                
    def move_up(self):
        """Move paddle up"""
        self.rect.y -= self.speed
        self.keep_in_bounds()
        
    def move_down(self):
        """Move paddle down"""
        self.rect.y += self.speed
        self.keep_in_bounds()
        
    def keep_in_bounds(self):
        """Keep paddle within screen bounds"""
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            
    def draw(self, surface):
        """Draw paddle"""
        pygame.draw.rect(surface, self.color, self.rect)
        # Draw border
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Add visual details
        if self.is_player_one:
            # Left paddle grip lines
            for i in range(1, 4):
                line_y = self.rect.top + self.rect.height * (i / 4)
                pygame.draw.line(
                    surface,
                    self.theme['background'],
                    (self.rect.left + 3, line_y),
                    (self.rect.right - 3, line_y),
                    1
                )
        else:
            # Right paddle grip lines
            for i in range(1, 4):
                line_y = self.rect.top + self.rect.height * (i / 4)
                pygame.draw.line(
                    surface,
                    self.theme['background'],
                    (self.rect.left + 3, line_y),
                    (self.rect.right - 3, line_y),
                    1
                )

class Ball:
    def __init__(self, theme):
        """Initialize ball"""
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - BALL_SIZE // 2,
            SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
            BALL_SIZE,
            BALL_SIZE
        )
        self.color = theme['projectile']
        self.dx = random.choice([-1, 1]) * BALL_SPEED_X
        self.dy = random.choice([-1, 1]) * BALL_SPEED_Y
        self.theme = theme
        self.reset_position()
        
    def update(self, left_paddle, right_paddle):
        """Update ball position and handle collisions"""
        # Move ball
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Bounce off top/bottom
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.dy = -self.dy
            # Play bounce sound
            pygame.mixer.Sound.play(pygame.mixer.Sound(self.get_bounce_sound()))
            
        # Check for scoring
        if self.rect.left <= 0:
            right_paddle.score += 1
            pygame.mixer.Sound.play(pygame.mixer.Sound(self.get_score_sound()))
            self.reset_position()
            return "right_score"
            
        elif self.rect.right >= SCREEN_WIDTH:
            left_paddle.score += 1
            pygame.mixer.Sound.play(pygame.mixer.Sound(self.get_score_sound()))
            self.reset_position()
            return "left_score"
            
        # Bounce off paddles
        if self.rect.colliderect(left_paddle.rect) and self.dx < 0:
            self.handle_paddle_collision(left_paddle)
            
        if self.rect.colliderect(right_paddle.rect) and self.dx > 0:
            self.handle_paddle_collision(right_paddle)
            
        return None
        
    def handle_paddle_collision(self, paddle):
        """Handle ball collision with a paddle"""
        # Reverse x direction
        self.dx = -self.dx
        
        # Adjust y velocity based on where the ball hit the paddle
        # This creates more interesting angles
        relative_y = (paddle.rect.centery - self.rect.centery) / (paddle.rect.height / 2)
        self.dy = -relative_y * BALL_SPEED_Y
        
        # Speed up slightly with each hit
        if abs(self.dx) < 15:  # Cap maximum speed
            self.dx *= 1.1
            
        # Play bounce sound
        pygame.mixer.Sound.play(pygame.mixer.Sound(self.get_bounce_sound()))
        
    def reset_position(self):
        """Reset ball to center"""
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.dx = random.choice([-1, 1]) * BALL_SPEED_X
        self.dy = random.choice([-1, 1]) * BALL_SPEED_Y
        
    def draw(self, surface):
        """Draw ball"""
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Add a shine effect
        pygame.draw.circle(
            surface,
            WHITE,
            (self.rect.left + 3, self.rect.top + 3),
            2
        )
        
    def get_bounce_sound(self):
        """Generate a simple bounce sound"""
        sound = pygame.mixer.Sound(pygame.mixer.Sound.play)
        sound.set_volume(0.2)
        return sound
        
    def get_score_sound(self):
        """Generate a simple score sound"""
        sound = pygame.mixer.Sound(pygame.mixer.Sound.play)
        sound.set_volume(0.4)
        return sound

def run_pong_game(theme):
    """Run the Pong game"""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()
    
    # Create fonts
    font = pygame.font.SysFont('Arial', 24)
    title_font = pygame.font.SysFont('Arial', 36, bold=True)
    score_font = pygame.font.SysFont('Arial', 48, bold=True)
    
    # Initialize game objects
    left_paddle = Paddle(
        30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH, PADDLE_HEIGHT, theme, True
    )
    
    right_paddle = Paddle(
        SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH, PADDLE_HEIGHT, theme, False
    )
    
    ball = Ball(theme)
    
    # Game states
    game_active = False
    game_over = False
    paused = False
    player_mode = "single"  # or "two_player"
    ai_difficulty = 1  # Default to medium
    winning_score = 5
    
    # Buttons
    one_player_button = Button(
        SCREEN_WIDTH // 2 - 220,
        SCREEN_HEIGHT // 2 - 20,
        200,
        50,
        "1 Player",
        GREEN
    )
    
    two_player_button = Button(
        SCREEN_WIDTH // 2 + 20,
        SCREEN_HEIGHT // 2 - 20,
        200,
        50,
        "2 Player",
        BLUE
    )
    
    difficulty_buttons = [
        Button(SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 + 50, 180, 40, "Easy", GREEN),
        Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 50, 180, 40, "Medium", BLUE),
        Button(SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2 + 50, 180, 40, "Hard", RED)
    ]
    
    # Start button
    start_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT // 2 + 120,
        200,
        50,
        "Start Game",
        GREEN
    )
    
    # Restart and menu buttons
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
        GRAY
    )
    
    # Get high score
    high_score = get_high_score("Pong")
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle key events
            if event.type == pygame.KEYDOWN:
                # Pause/unpause
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    if game_active:
                        paused = not paused
                
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Main menu
                if not game_active and not game_over:
                    # Mode selection
                    if one_player_button.is_clicked(mouse_pos):
                        player_mode = "single"
                    elif two_player_button.is_clicked(mouse_pos):
                        player_mode = "two_player"
                        
                    # Difficulty selection (only for single player)
                    if player_mode == "single":
                        for i, button in enumerate(difficulty_buttons):
                            if button.is_clicked(mouse_pos):
                                ai_difficulty = i
                    
                    # Start game
                    if start_button.is_clicked(mouse_pos):
                        game_active = True
                        # Reset everything
                        left_paddle.score = 0
                        right_paddle.score = 0
                        ball.reset_position()
                        
                # Game over screen
                elif game_over:
                    if restart_button.is_clicked(mouse_pos):
                        game_active = True
                        game_over = False
                        left_paddle.score = 0
                        right_paddle.score = 0
                        ball.reset_position()
                    elif menu_button.is_clicked(mouse_pos):
                        # Return to launcher with player's score
                        return left_paddle.score
                        
                # Pause button during gameplay
                elif game_active:
                    if pause_button.is_clicked(mouse_pos):
                        paused = not paused
        
        # Fill the screen
        screen.fill(theme['background'])
        
        # Draw middle line
        pygame.draw.aaline(
            screen,
            theme['text'],
            (SCREEN_WIDTH // 2, 0),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT)
        )
        
        # Draw middle circle
        pygame.draw.circle(
            screen,
            theme['text'],
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            50,
            1
        )
        
        # Main menu
        if not game_active and not game_over:
            # Draw title
            draw_text(
                screen,
                "PONG",
                title_font,
                theme['text'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 4
            )
            
            # Draw instructions based on selected mode
            if player_mode == "single":
                instructions = [
                    "Player 1: W/S keys to move paddle",
                    "First to 5 points wins!",
                    "Press ESC or P to pause"
                ]
            else:
                instructions = [
                    "Player 1: W/S keys",
                    "Player 2: Up/Down arrows",
                    "First to 5 points wins!",
                    "Press ESC or P to pause"
                ]
                
            for i, instruction in enumerate(instructions):
                draw_text(
                    screen,
                    instruction,
                    font,
                    theme['text'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 3 + i * 30
                )
                
            # Draw buttons
            one_player_button.draw(screen, theme)
            two_player_button.draw(screen, theme)
            
            # Highlight selected mode
            if player_mode == "single":
                pygame.draw.rect(screen, WHITE, one_player_button.rect, 3, border_radius=8)
            else:
                pygame.draw.rect(screen, WHITE, two_player_button.rect, 3, border_radius=8)
                
            # Draw difficulty buttons (only for single player)
            if player_mode == "single":
                draw_text(
                    screen,
                    "Select Difficulty:",
                    font,
                    theme['text'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 30
                )
                
                for i, button in enumerate(difficulty_buttons):
                    button.draw(screen, theme)
                    # Highlight selected difficulty
                    if i == ai_difficulty:
                        pygame.draw.rect(screen, WHITE, button.rect, 3, border_radius=8)
            
            # Draw start button
            start_button.draw(screen, theme)
            
        # Game over screen
        elif game_over:
            # Draw winner text
            if left_paddle.score >= winning_score:
                winner = "Player 1"
                winning_score = left_paddle.score
            else:
                if player_mode == "single":
                    winner = "Computer"
                else:
                    winner = "Player 2"
                winning_score = right_paddle.score
                
            draw_text(
                screen,
                f"{winner} Wins!",
                title_font,
                theme['accent1'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 3
            )
            
            # Draw final score
            draw_text(
                screen,
                f"{left_paddle.score} - {right_paddle.score}",
                score_font,
                theme['text'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 50
            )
            
            # Draw buttons
            restart_button.draw(screen, theme)
            menu_button.draw(screen, theme)
            
        # Active gameplay
        elif game_active:
            # Get keys
            keys = pygame.key.get_pressed()
            
            # Update paddles and ball if not paused
            if not paused:
                # Update left paddle (always player controlled)
                left_paddle.update(keys)
                
                # Update right paddle (player 2 or AI)
                if player_mode == "two_player":
                    right_paddle.update(keys)
                else:
                    right_paddle.update(None, ball, ai_difficulty)
                
                # Update ball and check for score
                result = ball.update(left_paddle, right_paddle)
                
                # Check if a player scored and update
                if result:
                    # Check for game over
                    if left_paddle.score >= winning_score or right_paddle.score >= winning_score:
                        game_active = False
                        game_over = True
                        
                        # Add score to leaderboard (player 1's score)
                        if left_paddle.score > high_score:
                            add_score("Pong", left_paddle.score)
                            high_score = left_paddle.score
            
            # Draw game elements
            left_paddle.draw(screen)
            right_paddle.draw(screen)
            ball.draw(screen)
            
            # Draw dividing line and circle (decorative)
            pygame.draw.aaline(screen, theme['text'], (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.circle(screen, theme['text'], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 50, 1)
            
            # Draw scores
            draw_text(
                screen,
                str(left_paddle.score),
                score_font,
                theme['text'],
                SCREEN_WIDTH // 4,
                50
            )
            
            draw_text(
                screen,
                str(right_paddle.score),
                score_font,
                theme['text'],
                3 * SCREEN_WIDTH // 4,
                50
            )
            
            # Draw mode/difficulty info
            if player_mode == "single":
                difficulty_names = ["Easy", "Medium", "Hard"]
                draw_text(
                    screen,
                    f"1P vs AI ({difficulty_names[ai_difficulty]})",
                    font,
                    theme['text'],
                    SCREEN_WIDTH // 2,
                    20
                )
            else:
                draw_text(
                    screen,
                    "2P vs 2P",
                    font,
                    theme['text'],
                    SCREEN_WIDTH // 2,
                    20
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
                if keys[pygame.K_BACKSPACE]:
                    return left_paddle.score
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    return left_paddle.score

if __name__ == "__main__":
    # For testing the game standalone
    from themes import DEFAULT_THEMES
    run_pong_game(DEFAULT_THEMES["Classic"])
