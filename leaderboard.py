"""
Leaderboard functionality for the Arcade Launcher
"""

import os
import json
import pygame
from pygame import gfxdraw
import time

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLES, WHITE, BLACK, GRAY, BLUE
from utils import draw_text, Button

def init_leaderboard():
    """Initialize the leaderboard file if it doesn't exist"""
    if not os.path.exists('leaderboard.json'):
        # Create an empty leaderboard file
        empty_leaderboard = {game: [] for game in GAME_TITLES}
        with open('leaderboard.json', 'w') as f:
            json.dump(empty_leaderboard, f, indent=4)

def load_leaderboard():
    """Load the leaderboard data from file"""
    try:
        with open('leaderboard.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is corrupt, initialize it
        init_leaderboard()
        return {game: [] for game in GAME_TITLES}

def display_leaderboard(screen, theme):
    """Display the leaderboard screen"""
    clock = pygame.time.Clock()
    running = True
    leaderboard_data = load_leaderboard()
    
    # Fonts
    title_font = pygame.font.SysFont('Arial', 36, bold=True)
    game_font = pygame.font.SysFont('Arial', 28, bold=True)
    score_font = pygame.font.SysFont('Arial', 24)
    
    # Current selected game
    current_game_index = 0
    
    # Back button
    back_button = Button(
        SCREEN_WIDTH // 2 - 100,
        SCREEN_HEIGHT - 70,
        200,
        50,
        "Back to Menu",
        BLUE
    )
    
    # Navigation buttons
    prev_button = Button(50, SCREEN_HEIGHT // 2, 100, 40, "Previous", GRAY)
    next_button = Button(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2, 100, 40, "Next", GRAY)
    
    while running:
        screen.fill(theme['background'])
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if back button is clicked
                if back_button.is_clicked(mouse_pos):
                    running = False
                    
                # Check navigation buttons
                if prev_button.is_clicked(mouse_pos):
                    current_game_index = (current_game_index - 1) % len(GAME_TITLES)
                    
                if next_button.is_clicked(mouse_pos):
                    current_game_index = (current_game_index + 1) % len(GAME_TITLES)
                    
            # Allow keyboard navigation as well
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_LEFT:
                    current_game_index = (current_game_index - 1) % len(GAME_TITLES)
                if event.key == pygame.K_RIGHT:
                    current_game_index = (current_game_index + 1) % len(GAME_TITLES)
        
        # Draw title
        draw_text(
            screen,
            "LEADERBOARD",
            title_font,
            theme['text'],
            SCREEN_WIDTH // 2,
            50
        )
        
        # Draw divider
        pygame.draw.rect(
            screen,
            theme['accent1'],
            (SCREEN_WIDTH // 2 - 300, 90, 600, 3)
        )
        
        # Draw current game title
        current_game = GAME_TITLES[current_game_index]
        draw_text(
            screen,
            current_game,
            game_font,
            theme['accent2'],
            SCREEN_WIDTH // 2,
            120
        )
        
        # Get scores for current game
        scores = leaderboard_data.get(current_game, [])
        scores = sorted(scores, reverse=True)[:5]  # Get top 5 scores
        
        # Draw scores
        if scores:
            for i, score in enumerate(scores):
                y_pos = 180 + i * 50
                # Draw rank
                draw_text(
                    screen,
                    f"{i+1}.",
                    score_font,
                    theme['text'],
                    SCREEN_WIDTH // 2 - 100,
                    y_pos,
                    align="right"
                )
                
                # Draw score
                draw_text(
                    screen,
                    f"{score}",
                    score_font,
                    theme['text'],
                    SCREEN_WIDTH // 2 + 100,
                    y_pos,
                    align="left"
                )
        else:
            # No scores yet
            draw_text(
                screen,
                "No scores yet!",
                score_font,
                theme['text'],
                SCREEN_WIDTH // 2,
                250
            )
            
            draw_text(
                screen,
                "Play the game to set a high score.",
                score_font,
                theme['text'],
                SCREEN_WIDTH // 2,
                300
            )
        
        # Draw navigation buttons
        prev_button.draw(screen, theme)
        next_button.draw(screen, theme)
        
        # Draw back button
        back_button.draw(screen, theme)
        
        # Draw navigation instructions
        instruction_font = pygame.font.SysFont('Arial', 16)
        draw_text(
            screen,
            "Use arrow keys or buttons to navigate between games",
            instruction_font,
            theme['text'],
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 120
        )
        
        pygame.display.flip()
        clock.tick(FPS)

def add_score(game_name, score):
    """Add a score to the leaderboard"""
    try:
        leaderboard = load_leaderboard()
        
        if game_name in leaderboard:
            # Add score and sort
            leaderboard[game_name].append(score)
            leaderboard[game_name] = sorted(leaderboard[game_name], reverse=True)[:5]
        else:
            # Create new entry
            leaderboard[game_name] = [score]
            
        with open('leaderboard.json', 'w') as f:
            json.dump(leaderboard, f, indent=4)
            
        return True
    except Exception as e:
        print(f"Error adding score: {e}")
        return False

def get_high_score(game_name):
    """Get the high score for a specific game"""
    leaderboard = load_leaderboard()
    scores = leaderboard.get(game_name, [])
    
    if scores:
        return max(scores)
    else:
        return 0
