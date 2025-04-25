"""
Utility functions and classes for the Arcade Launcher
"""

import pygame
from constants import (
    WHITE, BLACK, GRAY, BLUE, GREEN, RED, YELLOW, PURPLE,
    ORANGE, CYAN, GOLD, LIGHT_PURPLE, LIGHT_ORANGE, LIGHT_BLUE,
    DARK_BLUE, DARK_GREEN, DARK_RED, LIGHT_GREEN, LIGHT_RED, 
    LIGHT_YELLOW, DARK_GRAY, MAGENTA, PINK, BROWN, SILVER, BRONZE
)

def draw_text(surface, text, font, color, x, y, align="center"):
    """
    Draw text on a surface with alignment options
    
    Args:
        surface: Pygame surface to draw on
        text: String to display
        font: Pygame font object
        color: Text color (RGB tuple)
        x, y: Coordinates for text
        align: Text alignment ("left", "center", "right")
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    if align == "center":
        text_rect.center = (x, y)
    elif align == "left":
        text_rect.midleft = (x, y)
    elif align == "right":
        text_rect.midright = (x, y)
        
    surface.blit(text_surface, text_rect)
    return text_rect

class Button:
    """Enhanced Button class for menu navigation with visual effects"""
    
    def __init__(self, x, y, width, height, text, color, text_color=WHITE, 
                 style="standard", icon=None, font_size=24, font_name="Arial"):
        """Initialize button properties"""
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.hover = False
        self.font = pygame.font.SysFont(font_name, font_size)
        self.style = style  # "standard", "gradient", "glow", "3d"
        self.icon = icon    # Path to icon image or None
        self.icon_surface = None
        self.pressed = False
        self.animation_state = 0
        self.animation_direction = 1
        
        # Load icon if provided
        if self.icon:
            try:
                self.icon_surface = pygame.image.load(self.icon).convert_alpha()
                # Scale icon to fit button
                icon_size = min(width // 3, height - 10)
                self.icon_surface = pygame.transform.scale(self.icon_surface, (icon_size, icon_size))
            except:
                self.icon_surface = None
        
    def draw(self, surface, theme=None):
        """Draw the button on the given surface with enhanced visual effects"""
        # Use theme colors if provided
        button_color = self.color
        text_color = self.text_color
        
        if theme:
            button_color = theme.get('accent2', self.color)
            text_color = theme.get('text', self.text_color)
            
        # Calculate effect colors
        lighter_color = tuple(min(c + 50, 255) for c in button_color)
        darker_color = tuple(max(c - 50, 0) for c in button_color)
        
        # Animated pulse effect when hovering
        if self.hover:
            self.animation_state += 0.1 * self.animation_direction
            if self.animation_state > 1:
                self.animation_state = 1
                self.animation_direction = -1
            elif self.animation_state < 0:
                self.animation_state = 0
                self.animation_direction = 1
                
            pulse_factor = 0.2 * self.animation_state
            pulsed_color = tuple(min(int(c + pulse_factor * 50), 255) for c in button_color)
        else:
            self.animation_state = 0
            self.animation_direction = 1
            pulsed_color = button_color
            
        # Draw button based on style
        if self.style == "gradient":
            # Gradient effect
            if self.hover:
                draw_gradient_rect(surface, self.rect, lighter_color, button_color, 
                                  vertical=False, border_radius=12)
            else:
                draw_gradient_rect(surface, self.rect, button_color, darker_color, 
                                  vertical=False, border_radius=12)
            
            # Button border
            draw_rounded_rect(surface, self.rect, None, radius=12, 
                             border_color=BLACK, border_width=2)
            
        elif self.style == "3d":
            # 3D effect with shadow and highlight
            shadow_rect = self.rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            
            # Draw shadow first
            draw_rounded_rect(surface, shadow_rect, BLACK, radius=8)
            
            # Draw main button
            if self.pressed:
                # When pressed, move button down and use darker color
                button_rect = self.rect.copy()
                button_rect.x += 2
                button_rect.y += 2
                draw_rounded_rect(surface, button_rect, darker_color, radius=8)
            else:
                draw_rounded_rect(surface, self.rect, pulsed_color, radius=8)
                
            # Highlight on top edge when not pressed
            if not self.pressed:
                highlight_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 5)
                draw_rounded_rect(surface, highlight_rect, lighter_color, radius=8)
                
        elif self.style == "glow":
            # Glow effect
            # Draw base button
            draw_rounded_rect(surface, self.rect, button_color, radius=10)
            
            if self.hover:
                # Draw outer glow
                glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
                glow_rect = pygame.Rect(10, 10, self.rect.width, self.rect.height)
                
                for i in range(5, 0, -1):
                    glow_alpha = 50 - i * 10
                    glow_color = (*lighter_color, glow_alpha)
                    expanded_rect = glow_rect.inflate(i*2, i*2)
                    pygame.draw.rect(glow_surface, glow_color, expanded_rect, border_radius=10+i)
                
                surface.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
                
                # Re-draw button on top to avoid glow overlap
                draw_rounded_rect(surface, self.rect, pulsed_color, radius=10)
            
            # Button border
            draw_rounded_rect(surface, self.rect, None, radius=10, 
                             border_color=BLACK, border_width=2)
            
        else:  # Standard style
            # Button with hover effect
            if self.hover:
                draw_rounded_rect(surface, self.rect, pulsed_color, radius=8)
            else:
                draw_rounded_rect(surface, self.rect, button_color, radius=8)
                
            # Button border
            draw_rounded_rect(surface, self.rect, None, radius=8, 
                             border_color=BLACK, border_width=2)
        
        # Draw button text
        if self.style == "glow" and self.hover:
            # Glowing text on hover for glow style
            draw_glowing_text(
                surface, 
                self.text, 
                self.font, 
                text_color,
                lighter_color,  
                self.rect.centerx, 
                self.rect.centery,
                glow_radius=5
            )
        else:
            # Regular text with shadow for depth
            create_shadow_text(
                surface, 
                self.text, 
                self.font, 
                text_color, 
                BLACK,
                self.rect.centerx, 
                self.rect.centery,
                offset=2
            )
        
        # Draw icon if available
        if self.icon_surface:
            # Position icon to the left of text
            icon_x = self.rect.left + 10
            icon_y = self.rect.centery - self.icon_surface.get_height() // 2
            surface.blit(self.icon_surface, (icon_x, icon_y))
        
        # Update hover state
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos)
        
        # Update pressed state
        self.pressed = self.hover and pygame.mouse.get_pressed()[0]
        
    def is_clicked(self, pos):
        """Check if the button is clicked"""
        return self.rect.collidepoint(pos)

def draw_grid(surface, color, grid_size, width, height):
    """Draw a grid on the surface"""
    for x in range(0, width, grid_size):
        pygame.draw.line(surface, color, (x, 0), (x, height))
    for y in range(0, height, grid_size):
        pygame.draw.line(surface, color, (0, y), (width, y))
        
def center_rect(rect, screen_width, screen_height):
    """Center a rectangle on the screen"""
    rect.center = (screen_width // 2, screen_height // 2)
    return rect

def create_shadow_text(surface, text, font, color, shadow_color, x, y, offset=2):
    """Draw text with a shadow effect"""
    # Draw shadow
    shadow_surface = font.render(text, True, shadow_color)
    shadow_rect = shadow_surface.get_rect(center=(x + offset, y + offset))
    surface.blit(shadow_surface, shadow_rect)
    
    # Draw main text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)
    
    return text_rect

def draw_rounded_rect(surface, rect, color, radius=15, border_color=None, border_width=0):
    """Draw a rounded rectangle with optional border"""
    # Skip if color is None (just draw border)
    if color is not None:
        rect_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, color, rect_surface.get_rect(), border_radius=radius)
        surface.blit(rect_surface, rect)
    
    # Draw border if specified
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)
        
def draw_gradient_rect(surface, rect, color1, color2, vertical=True, border_radius=0):
    """Draw a rectangle with a gradient from color1 to color2"""
    rect_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    if vertical:
        for y in range(rect.height):
            # Calculate gradient color at this position
            ratio = y / float(rect.height)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(rect_surface, (r, g, b), (0, y), (rect.width, y))
    else:
        for x in range(rect.width):
            # Calculate gradient color at this position
            ratio = x / float(rect.width)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(rect_surface, (r, g, b), (x, 0), (x, rect.height))
    
    # Apply rounded corners if needed
    if border_radius > 0:
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), mask.get_rect(), border_radius=border_radius)
        rect_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
    surface.blit(rect_surface, rect)
    
def draw_glowing_text(surface, text, font, color, glow_color, x, y, glow_radius=5, align="center"):
    """Draw text with a glowing effect"""
    # Create surfaces for the glow effect
    glow_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    
    # Render text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    # Set alignment
    if align == "center":
        text_rect.center = (x, y)
    elif align == "left":
        text_rect.midleft = (x, y)
    elif align == "right":
        text_rect.midright = (x, y)
        
    # Draw glow (multiple blurred copies of the text)
    for i in range(1, glow_radius, 2):
        glow_text = font.render(text, True, glow_color)
        glow_rect = glow_text.get_rect()
        glow_rect.center = text_rect.center
        
        # Offset in all directions for the blur effect
        for dx, dy in [(-i, -i), (-i, 0), (-i, i), (0, -i), (0, i), (i, -i), (i, 0), (i, i)]:
            glow_rect = glow_text.get_rect()
            if align == "center":
                glow_rect.center = (x + dx, y + dy)
            elif align == "left":
                glow_rect.midleft = (x + dx, y + dy)
            elif align == "right":
                glow_rect.midright = (x + dx, y + dy)
            glow_surface.blit(glow_text, glow_rect)
            
    # Apply the glow with reduced alpha
    surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    
    # Draw the main text on top
    surface.blit(text_surface, text_rect)
    
    return text_rect
