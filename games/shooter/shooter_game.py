"""
Space Shooter Game Implementation
A classic space shooter where the player controls a spaceship to destroy enemies.
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
    WHITE, BLACK, BLUE, GREEN, RED, GRAY, YELLOW,
    PLAYER_SPEED, BULLET_SPEED, ENEMY_SPEED, ENEMY_FREQUENCY,
    PLAYER_SIZE, ENEMY_SIZE, BULLET_SIZE
)
from utils import draw_text, Button, create_shadow_text
from leaderboard import add_score, get_high_score

class Player:
    def __init__(self, theme):
        """Initialize the player's spaceship"""
        self.theme = theme
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - self.width // 2,
            SCREEN_HEIGHT - 100,
            self.width,
            self.height
        )
        self.color = theme['player']
        self.speed = PLAYER_SPEED
        self.shoot_cooldown = 0
        self.cooldown_time = 250  # ms between shots
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 2000  # 2 seconds of invulnerability after hit
        
    def update(self, keys):
        """Update player position based on key input"""
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Update invulnerability
        if self.invulnerable:
            if pygame.time.get_ticks() - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False
        
    def shoot(self):
        """Create a new bullet if cooldown allows"""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.cooldown_time
            return Bullet(self.rect.centerx, self.rect.top, self.theme)
        return None
        
    def get_hit(self):
        """Player gets hit by enemy"""
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            return True
        return False
        
    def draw(self, surface):
        """Draw the player's spaceship"""
        # Don't draw if invulnerable and in a blinking phase
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            return
            
        # Draw a triangle spaceship
        points = [
            (self.rect.centerx, self.rect.top),  # Nose
            (self.rect.left, self.rect.bottom),  # Bottom left
            (self.rect.right, self.rect.bottom)  # Bottom right
        ]
        pygame.draw.polygon(surface, self.color, points)
        
        # Add details (cockpit, engines)
        # Cockpit
        pygame.draw.circle(
            surface,
            self.theme['accent1'],
            (self.rect.centerx, self.rect.centery),
            self.width // 6
        )
        
        # Left engine
        pygame.draw.rect(
            surface,
            self.theme['accent2'],
            (self.rect.left + 5, self.rect.bottom - 8, 8, 12)
        )
        
        # Right engine
        pygame.draw.rect(
            surface,
            self.theme['accent2'],
            (self.rect.right - 13, self.rect.bottom - 8, 8, 12)
        )
        
        # Engine flames (animated)
        flame_height = random.randint(5, 15)
        flame_color = random.choice([YELLOW, ORANGE, RED])
        
        # Left engine flame
        pygame.draw.polygon(
            surface,
            flame_color,
            [
                (self.rect.left + 9, self.rect.bottom),
                (self.rect.left + 5, self.rect.bottom + flame_height),
                (self.rect.left + 13, self.rect.bottom + flame_height)
            ]
        )
        
        # Right engine flame
        pygame.draw.polygon(
            surface,
            flame_color,
            [
                (self.rect.right - 9, self.rect.bottom),
                (self.rect.right - 5, self.rect.bottom + flame_height),
                (self.rect.right - 13, self.rect.bottom + flame_height)
            ]
        )

class Bullet:
    def __init__(self, x, y, theme):
        """Initialize a bullet"""
        self.theme = theme
        self.radius = BULLET_SIZE
        self.rect = pygame.Rect(
            x - self.radius,
            y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        self.color = theme['projectile']
        self.speed = BULLET_SPEED
        
    def update(self):
        """Update bullet position"""
        self.rect.y -= self.speed
        return self.rect.bottom < 0  # Return True if off screen
        
    def draw(self, surface):
        """Draw the bullet"""
        pygame.draw.circle(
            surface,
            self.color,
            self.rect.center,
            self.radius
        )
        
        # Add glow effect
        pygame.draw.circle(
            surface,
            tuple(min(c + 50, 255) for c in self.color),
            self.rect.center,
            self.radius // 2
        )

class Enemy:
    def __init__(self, theme):
        """Initialize an enemy"""
        self.theme = theme
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE
        self.rect = pygame.Rect(
            random.randint(0, SCREEN_WIDTH - self.width),
            -self.height,
            self.width,
            self.height
        )
        self.color = theme['opponent']
        self.speed = random.uniform(ENEMY_SPEED, ENEMY_SPEED * 1.5)
        self.type = random.choice(['basic', 'zigzag', 'fast'])
        self.zigzag_direction = random.choice([-1, 1])
        self.zigzag_counter = 0
        self.points = 10
        
        # Adjust properties based on type
        if self.type == 'zigzag':
            self.points = 15
        elif self.type == 'fast':
            self.speed *= 1.5
            self.points = 20
            # Make fast enemies smaller and a different color
            self.width = int(self.width * 0.8)
            self.height = int(self.height * 0.8)
            self.rect.width = self.width
            self.rect.height = self.height
            self.color = tuple(min(c + 40, 255) for c in self.color)
        
    def update(self):
        """Update enemy position"""
        self.rect.y += self.speed
        
        # Different movement patterns based on type
        if self.type == 'zigzag':
            # Zigzag movement
            self.zigzag_counter += 1
            if self.zigzag_counter >= 20:
                self.zigzag_direction *= -1
                self.zigzag_counter = 0
            self.rect.x += self.zigzag_direction * 2
            
            # Keep within screen bounds
            if self.rect.left <= 0:
                self.zigzag_direction = 1
            elif self.rect.right >= SCREEN_WIDTH:
                self.zigzag_direction = -1
        
        # Return True if enemy is off screen
        return self.rect.top > SCREEN_HEIGHT
        
    def draw(self, surface):
        """Draw the enemy"""
        # Basic enemy is a simple circle/saucer shape
        if self.type == 'basic':
            pygame.draw.ellipse(
                surface,
                self.color,
                self.rect
            )
            # Add cockpit/dome
            pygame.draw.ellipse(
                surface,
                self.theme['accent1'],
                (
                    self.rect.centerx - self.width // 4,
                    self.rect.centery - self.height // 4,
                    self.width // 2,
                    self.height // 2
                )
            )
            
        # Zigzag enemy is a diamond shape
        elif self.type == 'zigzag':
            points = [
                (self.rect.centerx, self.rect.top),  # Top
                (self.rect.right, self.rect.centery),  # Right
                (self.rect.centerx, self.rect.bottom),  # Bottom
                (self.rect.left, self.rect.centery)  # Left
            ]
            pygame.draw.polygon(surface, self.color, points)
            # Add center detail
            pygame.draw.circle(
                surface,
                self.theme['accent2'],
                self.rect.center,
                self.width // 4
            )
            
        # Fast enemy is a smaller, streamlined shape
        elif self.type == 'fast':
            # Draw a triangle
            points = [
                (self.rect.centerx, self.rect.top),  # Top
                (self.rect.right, self.rect.bottom),  # Bottom right
                (self.rect.left, self.rect.bottom)  # Bottom left
            ]
            pygame.draw.polygon(surface, self.color, points)
            
            # Add stripe
            pygame.draw.line(
                surface,
                self.theme['accent1'],
                (self.rect.centerx, self.rect.top + 5),
                (self.rect.centerx, self.rect.bottom - 5),
                3
            )

class Star:
    def __init__(self):
        """Initialize a background star"""
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.2, 1.0)
        self.brightness = random.randint(150, 255)
        
    def update(self):
        """Update star position for parallax scrolling effect"""
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, surface):
        """Draw the star"""
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(
            surface,
            color,
            (int(self.x), int(self.y)),
            self.size
        )

class Explosion:
    def __init__(self, x, y, size=30):
        """Initialize an explosion effect"""
        self.x = x
        self.y = y
        self.size = size
        self.radius = 2
        self.max_radius = size
        self.growth_rate = 2
        self.fade_rate = 5
        self.color = (255, 200, 50)  # Yellow/orange
        self.alpha = 255
        self.particles = []
        
        # Create explosion particles
        for _ in range(10):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(1, 3)
            dx = speed * math.cos(angle)
            dy = speed * math.sin(angle)
            size = random.randint(2, 5)
            self.particles.append([x, y, dx, dy, size])
        
    def update(self):
        """Update explosion animation"""
        # Grow and fade main explosion
        self.radius += self.growth_rate
        self.alpha -= self.fade_rate
        
        # Update particles
        for p in self.particles:
            p[0] += p[2]  # x += dx
            p[1] += p[3]  # y += dy
        
        # Return True when explosion is complete
        return self.alpha <= 0
        
    def draw(self, surface):
        """Draw the explosion"""
        # Create a transparent surface for the main explosion
        s = pygame.Surface((self.max_radius*2, self.max_radius*2), pygame.SRCALPHA)
        center = (self.max_radius, self.max_radius)
        
        # Draw main ring
        pygame.draw.circle(
            s,
            (*self.color, self.alpha),
            center,
            self.radius,
            3
        )
        
        # Draw particles
        for p in self.particles:
            pygame.draw.circle(
                surface,
                (*self.color, self.alpha),
                (int(p[0]), int(p[1])),
                p[4]
            )
        
        # Draw to main surface
        surface.blit(s, (self.x - self.max_radius, self.y - self.max_radius))

def run_shooter_game(theme):
    """Run the Space Shooter game"""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Shooter")
    clock = pygame.time.Clock()
    
    # Create fonts
    font = pygame.font.SysFont('Arial', 24)
    title_font = pygame.font.SysFont('Arial', 36, bold=True)
    score_font = pygame.font.SysFont('Arial', 32, bold=True)
    
    # Initialize game objects
    player = Player(theme)
    bullets = []
    enemies = []
    stars = [Star() for _ in range(100)]  # Background stars
    explosions = []
    
    # Game states
    game_active = False
    game_over = False
    paused = False
    score = 0
    wave = 1
    enemy_count = 5  # Initial enemies per wave
    
    # Time tracking
    last_enemy_time = pygame.time.get_ticks()
    wave_start_time = 0
    
    # High score
    high_score = get_high_score("Space Shooter")
    
    # Create buttons
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
                # Space to shoot
                if event.key == pygame.K_SPACE:
                    if game_active and not paused:
                        bullet = player.shoot()
                        if bullet:
                            bullets.append(bullet)
                    # Start game with space
                    elif not game_active and not game_over:
                        game_active = True
                        wave_start_time = pygame.time.get_ticks()
                    # Restart game with space
                    elif game_over:
                        # Reset game
                        game_active = True
                        game_over = False
                        player = Player(theme)
                        bullets = []
                        enemies = []
                        explosions = []
                        score = 0
                        wave = 1
                        enemy_count = 5
                        wave_start_time = pygame.time.get_ticks()
                
                # Pause/unpause
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    if game_active:
                        paused = not paused
                        
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Shoot on click during gameplay
                if game_active and not paused:
                    bullet = player.shoot()
                    if bullet:
                        bullets.append(bullet)
                    
                # Start screen buttons
                if not game_active and not game_over:
                    if start_button.is_clicked(mouse_pos):
                        game_active = True
                        wave_start_time = pygame.time.get_ticks()
                        
                # Game over screen buttons
                elif game_over:
                    if restart_button.is_clicked(mouse_pos):
                        # Reset game
                        game_active = True
                        game_over = False
                        player = Player(theme)
                        bullets = []
                        enemies = []
                        explosions = []
                        score = 0
                        wave = 1
                        enemy_count = 5
                        wave_start_time = pygame.time.get_ticks()
                    elif menu_button.is_clicked(mouse_pos):
                        return score
                        
                # Pause button during gameplay
                elif game_active:
                    if pause_button.is_clicked(mouse_pos):
                        paused = not paused
        
        # Fill the screen with dark background
        screen.fill((5, 5, 20))  # Very dark blue, almost black
        
        # Update and draw stars (parallax background)
        for star in stars:
            if game_active and not paused:
                star.update()
            star.draw(screen)
        
        # Start screen
        if not game_active and not game_over:
            # Draw title
            create_shadow_text(
                screen,
                "SPACE SHOOTER",
                title_font,
                theme['text'],
                BLACK,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 4
            )
            
            # Draw sample player ship as mascot
            mascot_player = Player(theme)
            mascot_player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50)
            mascot_player.draw(screen)
            
            # Draw sample enemies
            for i in range(3):
                enemy = Enemy(theme)
                enemy.rect.center = (
                    SCREEN_WIDTH // 4 + (SCREEN_WIDTH // 2 * i // 2),
                    SCREEN_HEIGHT // 3 - 20
                )
                enemy.type = ['basic', 'zigzag', 'fast'][i]
                enemy.draw(screen)
            
            # Draw instructions
            instructions = [
                "Arrow keys or WASD to move",
                "SPACE or Click to shoot",
                "Destroy enemies to score points",
                "Press ESC or P to pause"
            ]
                
            for i, instruction in enumerate(instructions):
                draw_text(
                    screen,
                    instruction,
                    font,
                    theme['text'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 20 + i * 30
                )
                
            # Draw high score
            draw_text(
                screen,
                f"High Score: {high_score}",
                score_font,
                theme['accent1'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 100
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
            
            # Draw wave reached
            draw_text(
                screen,
                f"Wave: {wave}",
                font,
                theme['text'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 20
            )
            
            # Draw high score
            if score > high_score:
                draw_text(
                    screen,
                    "NEW HIGH SCORE!",
                    score_font,
                    theme['accent1'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 10
                )
                high_score = score
            else:
                draw_text(
                    screen,
                    f"High Score: {high_score}",
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
                # Update player
                player.update(keys)
                
                # Update bullets
                for bullet in bullets[:]:
                    if bullet.update():
                        bullets.remove(bullet)
                
                # Update enemies
                for enemy in enemies[:]:
                    if enemy.update():
                        enemies.remove(enemy)
                        # Penalty for missing an enemy
                        if score > 0:
                            score -= 1
                
                # Update explosions
                for explosion in explosions[:]:
                    if explosion.update():
                        explosions.remove(explosion)
                
                # Spawn new enemies
                current_time = pygame.time.get_ticks()
                if current_time - last_enemy_time > ENEMY_FREQUENCY:
                    if len(enemies) < enemy_count:
                        enemies.append(Enemy(theme))
                        last_enemy_time = current_time
                
                # Check for wave completion
                if current_time - wave_start_time > 20000:  # 20 seconds per wave
                    wave += 1
                    wave_start_time = current_time
                    enemy_count += 2  # Increase enemy count per wave
                    
                    # Give wave completion bonus
                    wave_bonus = wave * 50
                    score += wave_bonus
                    
                    # Create wave bonus text
                    # This would be a floating text effect in a more complete game
                
                # Check bullet-enemy collisions
                for bullet in bullets[:]:
                    for enemy in enemies[:]:
                        if bullet.rect.colliderect(enemy.rect):
                            # Add score based on enemy type
                            score += enemy.points
                            
                            # Create explosion
                            explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                            
                            # Remove bullet and enemy
                            if bullet in bullets:
                                bullets.remove(bullet)
                            if enemy in enemies:
                                enemies.remove(enemy)
                
                # Check player-enemy collisions
                for enemy in enemies[:]:
                    if player.rect.colliderect(enemy.rect):
                        if player.get_hit():
                            # Create explosion
                            explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                            
                            # Remove enemy
                            enemies.remove(enemy)
                            
                            # Check if game over
                            if player.lives <= 0:
                                game_active = False
                                game_over = True
                                
                                # Update high score
                                if score > high_score:
                                    add_score("Space Shooter", score)
            
            # Draw game elements
            # Draw bullets
            for bullet in bullets:
                bullet.draw(screen)
                
            # Draw enemies
            for enemy in enemies:
                enemy.draw(screen)
                
            # Draw player
            player.draw(screen)
            
            # Draw explosions
            for explosion in explosions:
                explosion.draw(screen)
            
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
            
            # Draw wave
            draw_text(
                screen,
                f"Wave: {wave}",
                font,
                theme['text'],
                100,
                50,
                align="left"
            )
            
            # Draw lives
            for i in range(player.lives):
                # Draw small ship icons
                ship_rect = pygame.Rect(
                    SCREEN_WIDTH - 30 - i * 35,
                    20,
                    20,
                    20
                )
                points = [
                    (ship_rect.centerx, ship_rect.top),
                    (ship_rect.left, ship_rect.bottom),
                    (ship_rect.right, ship_rect.bottom)
                ]
                pygame.draw.polygon(screen, theme['player'], points)
            
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

# Add missing imports
import math
from constants import ORANGE

if __name__ == "__main__":
    # For testing the game standalone
    from themes import DEFAULT_THEMES
    run_shooter_game(DEFAULT_THEMES["Classic"])
