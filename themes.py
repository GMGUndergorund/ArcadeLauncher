"""
Theme management for the Arcade Launcher
"""

import os
import json
from constants import WHITE, BLACK, BLUE, GREEN, RED, PURPLE, CYAN, ORANGE, YELLOW, PINK

# Default themes
DEFAULT_THEMES = {
    "Classic": {
        "name": "Classic",
        "background": (0, 0, 0),
        "text": (255, 255, 255),
        "accent1": (0, 100, 255),
        "accent2": (0, 180, 0),
        "player": (255, 255, 255),
        "opponent": (200, 200, 200),
        "obstacle": (255, 50, 50),
        "projectile": (255, 255, 0)
    },
    "Neon": {
        "name": "Neon",
        "background": (10, 10, 30),
        "text": (0, 255, 255),
        "accent1": (255, 0, 255),
        "accent2": (0, 255, 0),
        "player": (0, 255, 255),
        "opponent": (255, 0, 255),
        "obstacle": (255, 255, 0),
        "projectile": (0, 255, 0)
    },
    "Pastel": {
        "name": "Pastel",
        "background": (240, 240, 255),
        "text": (100, 100, 120),
        "accent1": (200, 180, 255),
        "accent2": (180, 230, 210),
        "player": (180, 210, 230),
        "opponent": (230, 180, 210),
        "obstacle": (255, 200, 200),
        "projectile": (230, 230, 180)
    },
    "Retro": {
        "name": "Retro",
        "background": (20, 20, 20),
        "text": (200, 200, 200),
        "accent1": (0, 180, 0),
        "accent2": (180, 50, 0),
        "player": (0, 220, 0),
        "opponent": (220, 180, 0),
        "obstacle": (220, 0, 0),
        "projectile": (220, 220, 0)
    },
    "Ocean": {
        "name": "Ocean",
        "background": (0, 30, 60),
        "text": (200, 230, 255),
        "accent1": (0, 150, 200),
        "accent2": (0, 200, 150),
        "player": (100, 200, 255),
        "opponent": (50, 150, 200),
        "obstacle": (200, 50, 50),
        "projectile": (200, 200, 50)
    }
}

def load_themes():
    """Load themes from file or use defaults"""
    # First try to load from file
    if os.path.exists('themes.json'):
        try:
            with open('themes.json', 'r') as f:
                themes = json.load(f)
                # Validate themes
                for theme_name, theme in themes.items():
                    required_keys = ["name", "background", "text", "accent1", "accent2", 
                                     "player", "opponent", "obstacle", "projectile"]
                    if not all(key in theme for key in required_keys):
                        print(f"Theme {theme_name} is missing required keys, using defaults")
                        themes = DEFAULT_THEMES
                        break
                return themes
        except (json.JSONDecodeError, FileNotFoundError):
            print("Error loading themes file, using defaults")
            
    # Save default themes if file doesn't exist
    with open('themes.json', 'w') as f:
        json.dump(DEFAULT_THEMES, f, indent=4)
    
    return DEFAULT_THEMES

def save_themes(themes):
    """Save themes to file"""
    try:
        with open('themes.json', 'w') as f:
            json.dump(themes, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving themes: {e}")
        return False

def get_current_theme(themes):
    """Get the current theme preference"""
    try:
        if os.path.exists('theme_preference.json'):
            with open('theme_preference.json', 'r') as f:
                preference = json.load(f)
                theme_name = preference.get('current_theme', 'Classic')
                if theme_name in themes:
                    return themes[theme_name]
    except:
        pass
    
    # Default to Classic theme
    return themes['Classic']

def create_custom_theme(name, colors):
    """Create a custom theme with the given colors"""
    themes = load_themes()
    
    # Create new theme
    new_theme = {
        "name": name,
        "background": colors.get("background", (0, 0, 0)),
        "text": colors.get("text", (255, 255, 255)),
        "accent1": colors.get("accent1", (0, 100, 255)),
        "accent2": colors.get("accent2", (0, 180, 0)),
        "player": colors.get("player", (255, 255, 255)),
        "opponent": colors.get("opponent", (200, 200, 200)),
        "obstacle": colors.get("obstacle", (255, 50, 50)),
        "projectile": colors.get("projectile", (255, 255, 0))
    }
    
    # Add to themes
    themes[name] = new_theme
    save_themes(themes)
    
    return new_theme
