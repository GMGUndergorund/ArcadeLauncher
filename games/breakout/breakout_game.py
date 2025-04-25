"""
Breakout Game Implementation
Classic brick-breaking game where the player controls a paddle to bounce a ball and break bricks.
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
    WHITE, BLACK, BLUE, GREEN, RED, YELLOW, ORANGE, PURPLE, CYAN,
    BRICK_WIDTH, BRICK_HEIGHT, BRICK_ROWS, BRICK_COLS,
    PADDLE_WIDTH_BREAKOUT, BALL_RADIUS
)
from utils import draw_text, Button, center_rect
from leaderboard import add_score, get_high_score

class Brick:
    def __init__(self, x, y, width, height, color, points=10, strength=1):
        """Initialize a brick"""
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.points = points
        self.strength = strength  # How many hits to break
        self.original_strength = strength
        
    def hit(self):
        """Register a hit on the brick"""
        self.strength -= 1
        # Adjust color based on remaining strength
        if self.original_strength > 1:
            # Create a lighter color for damaged bricks
            self.color = tuple(max(c - 40, 0) for c in self.color)
        return self.strength <= 0, self.points
        
    def draw(self, surface):
        """Draw the brick"""
        pygame.draw.rect(surface, self.color, self.rect)
        # Add 3D effect with darker edges
        pygame.draw.rect(surface, BLACK, self.rect, 1)
        
        # Add shine/highlight to top left
        highlight_rect = pygame.Rect(
            self.rect.x + 2,
            self.rect.y + 2,
            self.rect.width - 4,
            5
        )
        pygame.draw.rect(surface, tuple(min(c + 40, 255) for c in self.color), highlight_rect)

class Paddle:
    def __init__(self, theme):
        """Initialize the paddle"""
        self.width = PADDLE_WIDTH_BREAKOUT
        self.height = 15
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - self.width // 2,
            SCREEN_HEIGHT - 40,
            self.width,
            self.height
        )
        self.color = theme['player']
        self.speed = 10
        self.theme = theme
        
    def update(self, keys=None, mouse_control=True):
        """Update paddle position"""
        if mouse_control:
            # Mouse control
            mouse_x, _ = pygame.mouse.get_pos()
            self.rect.centerx = mouse_x
        elif keys:
            # Keyboard control
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
        
        # Keep paddle on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
    def draw(self, surface):
        """Draw the paddle"""
        pygame.draw.rect(surface, self.color, self.rect)
        # Add border
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Add grip lines
        for i in range(1, 5):
            x = self.rect.left + (self.rect.width * i) / 5
            pygame.draw.line(
                surface,
                self.theme['background'],
                (x, self.rect.top + 2),
                (x, self.rect.bottom - 2),
                1
            )

class Ball:
    def __init__(self, theme):
        """Initialize the ball"""
        self.radius = BALL_RADIUS
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - self.radius,
            SCREEN_HEIGHT // 2 - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        self.color = theme['projectile']
        self.dx = random.choice([-1, 1]) * 5
        self.dy = -5  # Start moving upward
        self.speed_increase = 0.05  # Ball speeds up slightly over time
        self.max_speed = 10
        self.attached = True  # Start attached to paddle
        self.theme = theme
        
    def update(self, paddle, bricks, powerups=None):
        """Update ball position and handle collisions"""
        # If attached to paddle, position on top of it
        if self.attached:
            self.rect.centerx = paddle.rect.centerx
            self.rect.bottom = paddle.rect.top
            return 0, []  # No change in score, no bricks broken
        
        # Store previous position for collision detection
        prev_x, prev_y = self.rect.x, self.rect.y
        
        # Move ball
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        score_change = 0
        broken_bricks = []
        
        # Check for wall collisions
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.dx = -self.dx
            # Add slight randomness for more interesting gameplay
            self.dy += random.uniform(-0.3, 0.3)
            
        if self.rect.top <= 0:
            self.dy = -self.dy
            # Add slight randomness
            self.dx += random.uniform(-0.3, 0.3)
            
        # Check for paddle collision
        if self.rect.colliderect(paddle.rect) and self.dy > 0:
            # Calculate bounce angle based on where the ball hit the paddle
            # Center of paddle = straight up, edges = more angle
            relative_x = (self.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
            self.dx = relative_x * 7  # Max horizontal speed
            self.dy = -abs(self.dy)  # Ensure upward movement
            
            # Ensure minimum vertical speed
            if abs(self.dy) < 3:
                self.dy = -3
                
        # Limit max speed
        self.dx = max(min(self.dx, self.max_speed), -self.max_speed)
        self.dy = max(min(self.dy, self.max_speed), -self.max_speed)
        
        # Check for brick collisions
        for brick in bricks[:]:
            if self.rect.colliderect(brick.rect):
                broken, points = brick.hit()
                if broken:
                    bricks.remove(brick)
                    broken_bricks.append(brick)
                    score_change += points
                
                # Calculate which side of the brick was hit
                dx_entry = 0
                dy_entry = 0
                
                if self.dx > 0:
                    dx_entry = brick.rect.left - (prev_x + self.rect.width)
                else:
                    dx_entry = prev_x - brick.rect.right
                    
                if self.dy > 0:
                    dy_entry = brick.rect.top - (prev_y + self.rect.height)
                else:
                    dy_entry = prev_y - brick.rect.bottom
                    
                # Determine bounce direction based on collision side
                if abs(dx_entry) < abs(dy_entry):
                    self.dx = -self.dx
                else:
                    self.dy = -self.dy
                
                # Only process one brick collision per frame
                break
        
        # Speed up the ball slightly over time
        self.dx *= (1 + self.speed_increase / 100)
        self.dy *= (1 + self.speed_increase / 100)
        
        return score_change, broken_bricks
        
    def reset(self, paddle):
        """Reset the ball to the paddle"""
        self.rect.centerx = paddle.rect.centerx
        self.rect.bottom = paddle.rect.top
        self.dx = random.choice([-1, 1]) * 5
        self.dy = -5
        self.attached = True
        
    def launch(self):
        """Launch the ball from the paddle"""
        if self.attached:
            self.attached = False
        
    def draw(self, surface):
        """Draw the ball"""
        pygame.draw.circle(
            surface,
            self.color,
            self.rect.center,
            self.radius
        )
        
        # Add shine/highlight
        pygame.draw.circle(
            surface,
            WHITE,
            (self.rect.centerx - self.radius // 2, self.rect.centery - self.radius // 2),
            self.radius // 3
        )

class PowerUp:
    def __init__(self, x, y, powerup_type, theme):
        """Initialize a power-up"""
        self.rect = pygame.Rect(x, y, 30, 15)
        self.type = powerup_type  # 'expand', 'shrink', 'extra_life', 'multi_ball'
        self.dy = 3  # Speed of falling
        self.theme = theme
        
        # Set color based on type
        if self.type == 'expand':
            self.color = GREEN
        elif self.type == 'shrink':
            self.color = RED
        elif self.type == 'extra_life':
            self.color = BLUE
        elif self.type == 'multi_ball':
            self.color = YELLOW
        else:
            self.color = WHITE
            
    def update(self):
        """Update power-up position"""
        self.rect.y += self.dy
        return self.rect.top > SCREEN_HEIGHT  # Return True if offscreen
        
    def draw(self, surface):
        """Draw the power-up"""
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw a symbol or letter based on type
        font = pygame.font.SysFont('Arial', 10)
        if self.type == 'expand':
            text = 'E+'
        elif self.type == 'shrink':
            text = 'S-'
        elif self.type == 'extra_life':
            text = 'L+'
        elif self.type == 'multi_ball':
            text = 'M+'
        else:
            text = '?'
            
        text_surf = font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

def create_bricks(theme):
    """Create a layout of bricks"""
    bricks = []
    
    # Colors based on row (from bottom to top)
    colors = [
        PURPLE, # 7 points
        RED,    # 6 points  
        ORANGE, # 5 points
        YELLOW, # 4 points
        GREEN,  # 3 points
        CYAN,   # 2 points
        BLUE,   # 1 point
    ]
    
    # Adapt colors to theme if needed
    if theme:
        # Create color variations based on the theme's accent colors
        base_color = theme['accent1']
        colors = []
        for i in range(BRICK_ROWS):
            # Create a gradient of colors
            factor = i / (BRICK_ROWS - 1)
            r = int(base_color[0] * (1 - factor) + theme['accent2'][0] * factor)
            g = int(base_color[1] * (1 - factor) + theme['accent2'][1] * factor)
            b = int(base_color[2] * (1 - factor) + theme['accent2'][2] * factor)
            colors.append((r, g, b))
    
    # Calculate spacing
    brick_spacing_x = 5
    brick_spacing_y = 5
    usable_width = SCREEN_WIDTH - brick_spacing_x * (BRICK_COLS + 1)
    brick_width = usable_width // BRICK_COLS
    
    # Create brick layout
    for row in range(BRICK_ROWS):
        color = colors[row % len(colors)]
        points = BRICK_ROWS - row  # Higher rows = more points
        
        # Some bricks require multiple hits based on row
        strength = 1
        if row < 2:  # Top two rows take 2 hits
            strength = 2
        
        for col in range(BRICK_COLS):
            x = brick_spacing_x + col * (brick_width + brick_spacing_x)
            y = 50 + row * (BRICK_HEIGHT + brick_spacing_y)
            brick = Brick(x, y, brick_width, BRICK_HEIGHT, color, points * 10, strength)
            bricks.append(brick)
            
    return bricks

def run_breakout_game(theme):
    """Run the Breakout game"""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout")
    clock = pygame.time.Clock()
    
    # Create fonts
    font = pygame.font.SysFont('Arial', 24)
    title_font = pygame.font.SysFont('Arial', 36, bold=True)
    score_font = pygame.font.SysFont('Arial', 28)
    
    # Initialize game objects
    paddle = Paddle(theme)
    ball = Ball(theme)
    bricks = create_bricks(theme)
    powerups = []
    
    # Game states
    game_active = False
    game_over = False
    paused = False
    score = 0
    lives = 3
    level = 1
    mouse_control = True  # Toggle between mouse and keyboard control
    
    # Start button
    start_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT // 2 + 50,
        200,
        50,
        "Start Game",
        GREEN
    )
    
    # Control toggle button
    control_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT // 2 + 120,
        200,
        50,
        "Mouse Control",
        BLUE
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
        theme['text']
    )
    
    # Get high score
    high_score = get_high_score("Breakout")
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle key events
            if event.type == pygame.KEYDOWN:
                # Space to launch ball
                if event.key == pygame.K_SPACE and game_active and ball.attached:
                    ball.launch()
                    
                # Pause/unpause
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    if game_active:
                        paused = not paused
                        
            # Handle mouse clicks for buttons and ball launch
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Start screen
                if not game_active and not game_over:
                    if start_button.is_clicked(mouse_pos):
                        game_active = True
                    elif control_button.is_clicked(mouse_pos):
                        mouse_control = not mouse_control
                        control_button.text = "Mouse Control" if mouse_control else "Keyboard Control"
                        
                # Launch ball with click
                elif game_active and ball.attached:
                    ball.launch()
                    
                # Game over screen
                elif game_over:
                    if restart_button.is_clicked(mouse_pos):
                        # Reset game
                        game_active = True
                        game_over = False
                        score = 0
                        lives = 3
                        level = 1
                        bricks = create_bricks(theme)
                        ball.reset(paddle)
                        powerups = []
                    elif menu_button.is_clicked(mouse_pos):
                        return score
                        
                # Pause button during gameplay
                elif game_active:
                    if pause_button.is_clicked(mouse_pos):
                        paused = not paused
        
        # Fill the screen
        screen.fill(theme['background'])
        
        # Start screen
        if not game_active and not game_over:
            # Draw title
            draw_text(
                screen,
                "BREAKOUT",
                title_font,
                theme['text'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 4
            )
            
            # Draw instructions
            if mouse_control:
                instructions = [
                    "Move paddle with the mouse",
                    "Click or press SPACE to launch the ball",
                    "Break all bricks to advance",
                    "Press ESC or P to pause"
                ]
            else:
                instructions = [
                    "Move paddle with LEFT/RIGHT arrow keys",
                    "Press SPACE to launch the ball",
                    "Break all bricks to advance",
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
                score_font,
                theme['accent1'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2
            )
                
            # Draw buttons
            start_button.draw(screen, theme)
            control_button.draw(screen, theme)
            
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
                f"Score: {score}",
                score_font,
                theme['text'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 50
            )
            
            # Draw level reached
            draw_text(
                screen,
                f"Level: {level}",
                font,
                theme['text'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 20
            )
            
            # High score
            if score > high_score:
                draw_text(
                    screen,
                    "NEW HIGH SCORE!",
                    score_font,
                    theme['accent1'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 10
                )
                
            # Draw buttons
            restart_button.draw(screen, theme)
            menu_button.draw(screen, theme)
            
        # Active gameplay
        elif game_active:
            # Get keys
            keys = pygame.key.get_pressed()
            
            # Update game objects if not paused
            if not paused:
                # Update paddle
                paddle.update(keys, mouse_control)
                
                # Update ball and check collisions
                points, broken_bricks = ball.update(paddle, bricks, powerups)
                score += points
                
                # Check for power-up spawns from broken bricks
                for brick in broken_bricks:
                    # 15% chance to spawn a power-up
                    if random.random() < 0.15:
                        powerup_type = random.choice(['expand', 'shrink', 'extra_life', 'multi_ball'])
                        powerup = PowerUp(brick.rect.centerx, brick.rect.centery, powerup_type, theme)
                        powerups.append(powerup)
                
                # Update power-ups
                for powerup in powerups[:]:
                    if powerup.update():
                        powerups.remove(powerup)
                    elif powerup.rect.colliderect(paddle.rect):
                        # Apply power-up effect
                        if powerup.type == 'expand':
                            paddle.width = min(paddle.width + 20, 200)
                            paddle.rect.width = paddle.width
                            paddle.rect.centerx = paddle.rect.centerx  # Keep same center
                        elif powerup.type == 'shrink':
                            paddle.width = max(paddle.width - 20, 40)
                            paddle.rect.width = paddle.width
                            paddle.rect.centerx = paddle.rect.centerx  # Keep same center
                        elif powerup.type == 'extra_life':
                            lives += 1
                        elif powerup.type == 'multi_ball':
                            # Would add multiple balls in a full implementation
                            pass
                        powerups.remove(powerup)
                
                # Check if ball is lost
                if ball.rect.top > SCREEN_HEIGHT:
                    lives -= 1
                    if lives <= 0:
                        game_active = False
                        game_over = True
                        
                        # Update high score
                        if score > high_score:
                            add_score("Breakout", score)
                    else:
                        # Reset ball
                        ball.reset(paddle)
                        
                # Check if level is complete
                if not bricks:
                    level += 1
                    # Reset ball and create new brick layout
                    ball.reset(paddle)
                    bricks = create_bricks(theme)
                    # Make ball faster with each level
                    ball.max_speed += 1
                    # Reset paddle size
                    paddle.width = PADDLE_WIDTH_BREAKOUT
                    paddle.rect.width = paddle.width
                    # Give bonus points for completing level
                    score += level * 100
            
            # Draw game elements
            # Draw bricks
            for brick in bricks:
                brick.draw(screen)
                
            # Draw power-ups
            for powerup in powerups:
                powerup.draw(screen)
                
            # Draw paddle and ball
            paddle.draw(screen)
            ball.draw(screen)
            
            # Draw UI elements
            # Draw score
            draw_text(
                screen,
                f"Score: {score}",
                font,
                theme['text'],
                100,
                20,
                align="left"
            )
            
            # Draw lives
            draw_text(
                screen,
                f"Lives: {lives}",
                font,
                theme['text'],
                100,
                50,
                align="left"
            )
            
            # Draw level
            draw_text(
                screen,
                f"Level: {level}",
                font,
                theme['text'],
                SCREEN_WIDTH - 100,
                20,
                align="right"
            )
            
            # Draw launch instruction if ball is attached
            if ball.attached:
                draw_text(
                    screen,
                    "Click or Press SPACE to Launch",
                    font,
                    theme['text'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT - 20
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
                    return score
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    return score

if __name__ == "__main__":
    # For testing the game standalone
    from themes import DEFAULT_THEMES
    run_breakout_game(DEFAULT_THEMES["Classic"])
