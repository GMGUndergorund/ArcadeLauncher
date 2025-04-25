"""
Snake Game Implementation
Classic snake game where the player controls a snake to eat food and grow longer.
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
    WHITE, BLACK, GREEN, RED, BLUE, GRAY,
    SNAKE_GRID_SIZE, SNAKE_SPEED
)
from utils import draw_text, Button, draw_grid
from leaderboard import add_score, get_high_score

class Snake:
    def __init__(self, theme):
        """Initialize the snake"""
        self.theme = theme
        self.reset()
        
    def reset(self):
        """Reset the snake to starting position"""
        self.length = 3
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.score = 0
        self.grow_to = 3  # Initial length
        self.dead = False
        
    def update(self):
        """Update snake position"""
        if self.dead:
            return
            
        # Calculate new head position
        head = self.positions[0]
        dx, dy = self.direction
        new_head = (
            (head[0] + dx * SNAKE_GRID_SIZE) % SCREEN_WIDTH,
            (head[1] + dy * SNAKE_GRID_SIZE) % SCREEN_HEIGHT
        )
        
        # Check if snake hits itself
        if new_head in self.positions:
            self.dead = True
            return
            
        # Add new head
        self.positions.insert(0, new_head)
        
        # Remove tail if not growing
        if len(self.positions) > self.grow_to:
            self.positions.pop()
            
    def change_direction(self, direction):
        """Change snake direction"""
        # Prevent 180-degree turns
        dx, dy = direction
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)
            
    def grow(self):
        """Make the snake grow"""
        self.grow_to += 1
        self.score += 10
        
    def draw(self, surface):
        """Draw the snake"""
        # Draw snake body
        for i, pos in enumerate(self.positions):
            # Make head a different color
            if i == 0:
                color = self.theme['accent1']
            else:
                color = self.theme['player']
                
            # Draw segment
            rect = pygame.Rect(
                pos[0], pos[1],
                SNAKE_GRID_SIZE, SNAKE_GRID_SIZE
            )
            pygame.draw.rect(surface, color, rect)
            
            # Draw segment border
            pygame.draw.rect(surface, BLACK, rect, 1)
        
        # Draw eyes on head (if snake is big enough)
        if self.positions:
            head = self.positions[0]
            head_rect = pygame.Rect(
                head[0], head[1],
                SNAKE_GRID_SIZE, SNAKE_GRID_SIZE
            )
            
            # Determine eye positions based on direction
            dx, dy = self.direction
            if dx == 1:  # Right
                eye1 = (head_rect.right - 5, head_rect.top + 5)
                eye2 = (head_rect.right - 5, head_rect.bottom - 5)
            elif dx == -1:  # Left
                eye1 = (head_rect.left + 5, head_rect.top + 5)
                eye2 = (head_rect.left + 5, head_rect.bottom - 5)
            elif dy == 1:  # Down
                eye1 = (head_rect.left + 5, head_rect.bottom - 5)
                eye2 = (head_rect.right - 5, head_rect.bottom - 5)
            else:  # Up
                eye1 = (head_rect.left + 5, head_rect.top + 5)
                eye2 = (head_rect.right - 5, head_rect.top + 5)
                
            # Draw eyes
            pygame.draw.circle(surface, BLACK, eye1, 2)
            pygame.draw.circle(surface, BLACK, eye2, 2)
            
class Food:
    def __init__(self, theme):
        """Initialize food"""
        self.theme = theme
        self.position = (0, 0)
        self.reset()
        
    def reset(self):
        """Place food at a random position"""
        self.position = (
            random.randint(0, (SCREEN_WIDTH // SNAKE_GRID_SIZE) - 1) * SNAKE_GRID_SIZE,
            random.randint(0, (SCREEN_HEIGHT // SNAKE_GRID_SIZE) - 1) * SNAKE_GRID_SIZE
        )
        
    def draw(self, surface):
        """Draw the food"""
        rect = pygame.Rect(
            self.position[0], self.position[1],
            SNAKE_GRID_SIZE, SNAKE_GRID_SIZE
        )
        pygame.draw.rect(surface, self.theme['obstacle'], rect)
        
        # Add shine effect
        pygame.draw.circle(
            surface,
            WHITE,
            (rect.left + 5, rect.top + 5),
            2
        )

def run_snake_game(theme):
    """Run the Snake game"""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    
    # Create fonts
    font = pygame.font.SysFont('Arial', 24)
    title_font = pygame.font.SysFont('Arial', 36, bold=True)
    subtitle_font = pygame.font.SysFont('Arial', 28)
    
    # Initialize game objects
    snake = Snake(theme)
    food = Food(theme)
    
    # Game states
    game_active = False
    game_over = False
    paused = False
    
    # Start button
    start_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT // 2 + 50,
        200,
        50,
        "Start Game",
        GREEN
    )
    
    # Restart button for game over
    restart_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT // 2 + 20,
        200,
        50,
        "Play Again",
        GREEN
    )
    
    # Menu button for game over
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
    high_score = get_high_score("Snake")
    
    # Track last update time for movement
    last_update = time.time()
    update_delay = 1.0 / SNAKE_SPEED  # seconds per movement
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle key events
            if event.type == pygame.KEYDOWN:
                if game_active and not paused:
                    if event.key == pygame.K_UP:
                        snake.change_direction((0, -1))
                    if event.key == pygame.K_DOWN:
                        snake.change_direction((0, 1))
                    if event.key == pygame.K_LEFT:
                        snake.change_direction((-1, 0))
                    if event.key == pygame.K_RIGHT:
                        snake.change_direction((1, 0))
                        
                # Pause/unpause
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    if game_active:
                        paused = not paused
                        
                # Start new game if not active
                if not game_active and event.key == pygame.K_RETURN:
                    game_active = True
                    game_over = False
                    snake.reset()
                    food.reset()
                    
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Start screen
                if not game_active and not game_over:
                    if start_button.is_clicked(mouse_pos):
                        game_active = True
                        
                # Game over screen
                elif game_over:
                    if restart_button.is_clicked(mouse_pos):
                        game_active = True
                        game_over = False
                        snake.reset()
                        food.reset()
                    elif menu_button.is_clicked(mouse_pos):
                        return snake.score
                        
                # Pause button during gameplay
                elif game_active:
                    if pause_button.is_clicked(mouse_pos):
                        paused = not paused
        
        # Fill the screen
        screen.fill(theme['background'])
        
        # Grid background (faint)
        grid_color = list(theme['background'])
        grid_color = [min(c + 20, 255) for c in grid_color]  # Slightly lighter than background
        draw_grid(screen, tuple(grid_color), SNAKE_GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Start screen
        if not game_active and not game_over:
            # Draw title
            draw_text(
                screen,
                "SNAKE",
                title_font,
                theme['text'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 4
            )
            
            # Draw instructions
            instructions = [
                "Use arrow keys to control the snake",
                "Eat the food to grow longer",
                "Avoid hitting yourself",
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
                
            # Draw high score
            draw_text(
                screen,
                f"High Score: {high_score}",
                subtitle_font,
                theme['accent1'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2
            )
                
            # Draw start button
            start_button.draw(screen, theme)
            
        # Game over screen
        elif game_over:
            # Draw game over text
            draw_text(
                screen,
                "GAME OVER",
                title_font,
                RED,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 3
            )
            
            # Draw score
            draw_text(
                screen,
                f"Score: {snake.score}",
                subtitle_font,
                theme['text'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 50
            )
            
            # Draw high score
            if snake.score > high_score:
                draw_text(
                    screen,
                    "NEW HIGH SCORE!",
                    subtitle_font,
                    theme['accent1'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 15
                )
                high_score = snake.score
            else:
                draw_text(
                    screen,
                    f"High Score: {high_score}",
                    subtitle_font,
                    theme['accent1'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 15
                )
                
            # Draw buttons
            restart_button.draw(screen, theme)
            menu_button.draw(screen, theme)
            
        # Active gameplay
        elif game_active:
            # Update game state if not paused
            if not paused:
                current_time = time.time()
                if current_time - last_update > update_delay:
                    # Update snake
                    snake.update()
                    last_update = current_time
                    
                    # Check if snake is dead
                    if snake.dead:
                        game_active = False
                        game_over = True
                        add_score("Snake", snake.score)
                    
                    # Check if snake ate food
                    if snake.positions[0] == food.position:
                        snake.grow()
                        food.reset()
                        
                        # Make sure food doesn't spawn on snake
                        while food.position in snake.positions:
                            food.reset()
            
            # Draw game elements
            snake.draw(screen)
            food.draw(screen)
            
            # Draw score
            score_text = f"Score: {snake.score}"
            draw_text(
                screen,
                score_text,
                font,
                theme['text'],
                100,
                20,
                align="left"
            )
            
            # Draw high score
            high_score_text = f"High Score: {high_score}"
            draw_text(
                screen,
                high_score_text,
                font,
                theme['text'],
                100,
                50,
                align="left"
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
                    return snake.score
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    return snake.score

if __name__ == "__main__":
    # For testing the game standalone
    from themes import DEFAULT_THEMES
    run_snake_game(DEFAULT_THEMES["Classic"])
