import pygame

class Config:

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    
    COLORS = {
        'BACKGROUND': (70, 130, 180),  # Steel blue
        'UNCOLORED': (200, 200, 255),  # Light blue-gray
        'BORDER': (0, 0, 0),           # Black
        'UI_BACKGROUND': (240, 240, 240),  # Light gray
        'TEXT': (0, 0, 0),             # Black
        'BUTTON_HOVER': (220, 220, 220),  # Light gray
    }
    
    UI_HEIGHT = 80
    COLOR_BUTTON_SIZE = 50
    BUTTON_MARGIN = 10
    
    BORDER_WIDTH = 2
    REGION_HOVER_ALPHA = 50

    DEFAULT_ZOOM = 1.0
    MIN_ZOOM = 0.5
    MAX_ZOOM = 10.0
    ZOOM_SPEED = 0.1

    DEFAULT_GAME_COLORS = [
        (255, 99, 71),   # Red/Tomato
        (100, 149, 237), # Blue/Cornflower
        (255, 215, 0),   # Gold
        (50, 205, 50)    # Green/Lime
    ]
    
    # Current game colors (can be customized)
    GAME_COLORS = DEFAULT_GAME_COLORS.copy()
    
    @staticmethod
    def reset_colors():
        """Reset colors to defaults."""
        Config.GAME_COLORS = Config.DEFAULT_GAME_COLORS.copy()