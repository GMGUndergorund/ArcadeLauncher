#!/usr/bin/env python3
"""
Arcade Launcher - Main Application
A Python-based arcade launcher featuring multiple classic mini-games
"""

import os
import sys
import json
import pygame
from pygame import gfxdraw

# Local imports
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLES, 
    WHITE, BLACK, GRAY, BLUE, GREEN, RED, YELLOW, PURPLE,
    ORANGE, CYAN, GOLD, LIGHT_PURPLE, LIGHT_ORANGE, LIGHT_BLUE,
    DARK_BLUE, DARK_GREEN, DARK_RED, LIGHT_GREEN, LIGHT_RED, 
    LIGHT_YELLOW, DARK_GRAY, MAGENTA, PINK, BROWN, SILVER, BRONZE
)
from utils import (
    draw_text, Button, create_shadow_text, draw_rounded_rect,
    draw_gradient_rect, draw_glowing_text
)
from leaderboard import display_leaderboard, init_leaderboard
from themes import load_themes, get_current_theme

# Import games
from games.snake.snake_game import run_snake_game
from games.pong.pong_game import run_pong_game
from games.breakout.breakout_game import run_breakout_game
from games.flappy.flappy_game import run_flappy_game
from games.shooter.shooter_game import run_shooter_game

class ArcadeLauncher:
    def __init__(self):
        """Initialize the Arcade Launcher"""
        # Setup
        pygame.init()
        pygame.display.set_caption("Python Arcade Launcher")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize leaderboard file if it doesn't exist
        init_leaderboard()
        
        # Load themes
        self.themes = load_themes()
        self.current_theme = get_current_theme(self.themes)
        
        # Game buttons
        self.buttons = []
        
        # Main menu elements
        self.create_menu_buttons()

    def create_menu_buttons(self):
        """Create the main menu buttons with enhanced visuals"""
        button_width, button_height = 300, 60
        spacing = 20
        start_y = SCREEN_HEIGHT // 4
        
        # Button styles for different game categories
        action_styles = ["gradient", "3d", "glow"]
        puzzle_styles = ["gradient", "3d", "glow"]  
        
        # Game launch buttons in a grid layout (2 columns)
        self.buttons = []
        num_games = len(GAME_TITLES)
        games_per_column = (num_games + 1) // 2  # Ceiling division
        
        for i, game in enumerate(GAME_TITLES):
            # Determine column and position
            col = i // games_per_column
            row = i % games_per_column
            
            # Calculate x and y positions
            x_pos = SCREEN_WIDTH // 4 + col * (button_width + spacing)
            y_pos = start_y + row * (button_height + spacing)
            
            # Choose style based on game type
            if i < 5:  # Original games
                style = "standard"
            elif i < 7:  # First two new games
                style = "gradient"
            else:  # Last new game
                style = "glow"
                
            # Choose color based on game category
            if i == 0:  # Snake
                color = GREEN
            elif i in [1, 3]:  # Pong, Flappy Bird
                color = BLUE
            elif i == 2:  # Breakout
                color = ORANGE  
            elif i == 4:  # Space Shooter
                color = RED
            elif i == 5:  # Tetris
                color = PURPLE
            elif i == 6:  # Pac-Man
                color = YELLOW
            elif i == 7:  # Racing
                color = CYAN
            else:
                color = GRAY
                
            # Create button with appropriate style
            self.buttons.append(
                Button(
                    x_pos - button_width // 2,
                    y_pos,
                    button_width,
                    button_height,
                    game,
                    color,
                    WHITE,
                    style=style,
                    font_size=24
                )
            )
            
        # Bottom row buttons with special effects
        bottom_y = start_y + games_per_column * (button_height + spacing) + spacing * 2
        
        # Leaderboard button
        self.leaderboard_button = Button(
            SCREEN_WIDTH // 4 - button_width // 2,
            bottom_y,
            button_width,
            button_height,
            "Leaderboard",
            GOLD,
            style="gradient",
            font_size=24
        )
        
        # Theme button
        self.theme_button = Button(
            SCREEN_WIDTH // 2 + SCREEN_WIDTH // 4 - button_width // 2,
            bottom_y,
            button_width,
            button_height,
            "Change Theme",
            LIGHT_PURPLE,
            style="3d",
            font_size=24
        )
        
        # Exit button
        self.exit_button = Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            bottom_y + button_height + spacing,
            button_width,
            button_height,
            "Exit",
            RED,
            style="glow",
            font_size=24
        )

    def handle_events(self):
        """Handle user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check for button clicks
                mouse_pos = pygame.mouse.get_pos()
                
                # Game buttons
                for i, button in enumerate(self.buttons):
                    if button.is_clicked(mouse_pos):
                        self.launch_game(i)
                
                # Leaderboard button
                if self.leaderboard_button.is_clicked(mouse_pos):
                    self.show_leaderboard()
                
                # Theme button
                if self.theme_button.is_clicked(mouse_pos):
                    self.cycle_theme()
                
                # Exit button
                if self.exit_button.is_clicked(mouse_pos):
                    self.running = False

    def launch_game(self, game_index):
        """Launch the selected game"""
        pygame.display.quit()
        
        score = None
        
        # Run the selected game
        if game_index == 0:
            score = run_snake_game(self.current_theme)
        elif game_index == 1:
            score = run_pong_game(self.current_theme)
        elif game_index == 2:
            score = run_breakout_game(self.current_theme)
        elif game_index == 3:
            score = run_flappy_game(self.current_theme)
        elif game_index == 4:
            score = run_shooter_game(self.current_theme)
        elif game_index == 5:
            # Placeholder for Tetris game - will implement in a future update
            # Import will be added when implemented
            self.display_coming_soon("Tetris")
            return
        elif game_index == 6:
            # Placeholder for Pac-Man game - will implement in a future update
            # Import will be added when implemented
            self.display_coming_soon("Pac-Man")
            return
        elif game_index == 7:
            # Placeholder for Racing game - will implement in a future update
            # Import will be added when implemented
            self.display_coming_soon("Racing")
            return
        
        # Reinitialize the main screen
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Arcade Launcher")
        
        # Update leaderboard with the score if applicable
        if score is not None:
            self.update_leaderboard(GAME_TITLES[game_index], score)
            
    def display_coming_soon(self, game_name):
        """Display a coming soon message for games under development"""
        # Create a temporary screen
        temp_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"{game_name} - Coming Soon")
        temp_clock = pygame.time.Clock()
        
        # Create font objects
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        message_font = pygame.font.SysFont('Arial', 28)
        instruction_font = pygame.font.SysFont('Arial', 22)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                    
            # Fill background with gradient
            background_top = self.current_theme['background']
            background_bottom = tuple(max(0, c - 50) for c in background_top)
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                r = int(background_top[0] * (1 - ratio) + background_bottom[0] * ratio)
                g = int(background_top[1] * (1 - ratio) + background_bottom[1] * ratio)
                b = int(background_top[2] * (1 - ratio) + background_bottom[2] * ratio)
                pygame.draw.line(temp_screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
            # Draw message
            draw_glowing_text(
                temp_screen,
                f"{game_name}",
                title_font,
                self.current_theme['text'],
                self.current_theme['accent1'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 3,
                glow_radius=8
            )
            
            draw_text(
                temp_screen,
                "COMING SOON",
                message_font,
                self.current_theme['accent2'],
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2
            )
            
            # Add some visual interest - animated dots
            dot_count = (int(pygame.time.get_ticks() / 500) % 4) + 1  # 1-4 dots
            dot_text = "." * dot_count
            try:
                draw_text(
                    temp_screen,
                    f"In Development{dot_text}",
                    message_font,
                    self.current_theme['text'],
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 50
                )
            except Exception as e:
                print(f"Error drawing animated text: {e}")
            
            # Draw instruction
            create_shadow_text(
                temp_screen,
                "Click or press any key to return to the menu",
                instruction_font,
                self.current_theme['text'],
                BLACK,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT - 100
            )
            
            pygame.display.flip()
            temp_clock.tick(FPS)
        
        # Reinitialize the main screen
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Arcade Launcher")

    def update_leaderboard(self, game_name, score):
        """Update the leaderboard with a new score"""
        try:
            with open('leaderboard.json', 'r') as f:
                leaderboard = json.load(f)
                
            if game_name in leaderboard:
                # Check if the score is high enough to be in the top 5
                leaderboard[game_name].append(score)
                leaderboard[game_name] = sorted(leaderboard[game_name], reverse=True)[:5]
            else:
                leaderboard[game_name] = [score]
                
            with open('leaderboard.json', 'w') as f:
                json.dump(leaderboard, f, indent=4)
        except Exception as e:
            print(f"Error updating leaderboard: {e}")

    def show_leaderboard(self):
        """Display the leaderboard screen"""
        display_leaderboard(self.screen, self.current_theme)

    def cycle_theme(self):
        """Change to the next available theme"""
        theme_names = list(self.themes.keys())
        current_index = theme_names.index(self.current_theme['name'])
        next_index = (current_index + 1) % len(theme_names)
        self.current_theme = self.themes[theme_names[next_index]]
        
        # Save the current theme preference
        try:
            with open('theme_preference.json', 'w') as f:
                json.dump({"current_theme": self.current_theme['name']}, f)
        except Exception as e:
            print(f"Error saving theme preference: {e}")

    def draw(self):
        """Draw the main menu screen with enhanced visuals"""
        # Create a gradient background based on theme
        background_top = self.current_theme['background']
        background_bottom = tuple(max(0, c - 30) for c in background_top)  # Slightly darker at bottom
        
        # Draw gradient background
        for y in range(SCREEN_HEIGHT):
            # Calculate color at this position
            ratio = y / SCREEN_HEIGHT
            r = int(background_top[0] * (1 - ratio) + background_bottom[0] * ratio)
            g = int(background_top[1] * (1 - ratio) + background_bottom[1] * ratio)
            b = int(background_top[2] * (1 - ratio) + background_bottom[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Add decorative grid pattern
        grid_color = tuple(min(c + 15, 255) for c in self.current_theme['background'])
        self.draw_background_grid(grid_color, 40)
        
        # Draw header bar
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 120)
        header_color = tuple(max(0, c - 20) for c in self.current_theme['background'])
        draw_gradient_rect(self.screen, header_rect, header_color, 
                         tuple(max(0, c - 40) for c in self.current_theme['background']),
                         vertical=True)
        
        # Draw title with glow effect
        title_font = pygame.font.SysFont('Arial', 52, bold=True)
        glow_color = self.current_theme.get('accent1', (0, 100, 255))
        draw_glowing_text(
            self.screen, 
            "PYTHON ARCADE LAUNCHER", 
            title_font, 
            self.current_theme['text'],
            glow_color,
            SCREEN_WIDTH // 2, 
            60,
            glow_radius=7
        )
        
        # Draw stylish decorative line
        line_y = 105
        line_width = 700
        line_height = 4
        accent_color = self.current_theme['accent1']
        
        # Draw gradient line
        grad_rect = pygame.Rect(SCREEN_WIDTH // 2 - line_width // 2, line_y, line_width, line_height)
        lighter_accent = tuple(min(c + 70, 255) for c in accent_color)
        draw_gradient_rect(self.screen, grad_rect, lighter_accent, accent_color, vertical=False)
        
        # Add line details
        for x in range(SCREEN_WIDTH // 2 - line_width // 2, SCREEN_WIDTH // 2 + line_width // 2, 50):
            dot_size = 3
            pygame.draw.circle(self.screen, WHITE, (x, line_y + line_height // 2), dot_size)
        
        # Draw all game buttons
        for button in self.buttons:
            button.draw(self.screen, self.current_theme)
            
        # Draw utility buttons
        self.leaderboard_button.draw(self.screen, self.current_theme)
        self.theme_button.draw(self.screen, self.current_theme)
        self.exit_button.draw(self.screen, self.current_theme)
        
        # Draw footer bar
        footer_rect = pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        footer_color = tuple(max(0, c - 20) for c in self.current_theme['background'])
        draw_gradient_rect(self.screen, footer_rect, 
                         tuple(max(0, c - 40) for c in self.current_theme['background']),
                         footer_color, vertical=True)
        
        # Draw current theme name with shadow
        theme_font = pygame.font.SysFont('Arial', 16)
        create_shadow_text(
            self.screen,
            f"Current Theme: {self.current_theme['name']}",
            theme_font,
            self.current_theme['text'],
            BLACK,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 25
        )
        
        # Draw version number
        version_text = "v1.2"
        create_shadow_text(
            self.screen,
            version_text,
            theme_font,
            self.current_theme['text'],
            BLACK,
            SCREEN_WIDTH - 50,
            SCREEN_HEIGHT - 25
        )
        
        # Update the display
        pygame.display.flip()
        
    def draw_background_grid(self, color, grid_size):
        """Draw a subtle background grid pattern"""
        for x in range(0, SCREEN_WIDTH, grid_size):
            pygame.draw.line(self.screen, color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y), 1)

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    print("Starting Arcade Launcher...")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if running from the correct directory
    if not os.path.exists('leaderboard.json') and os.path.exists('../leaderboard.json'):
        print("Changing to parent directory...")
        os.chdir('..')
    
    print(f"Working directory after check: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    # Create and run the launcher
    try:
        print("Initializing launcher...")
        app = ArcadeLauncher()
        print("Starting main loop...")
        app.run()
    except Exception as e:
        print(f"Error running launcher: {e}")
        import traceback
        traceback.print_exc()
