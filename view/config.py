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
    
    GAME_COLORS = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green  
        (255, 255, 0),  # Yellow
        (128, 0, 128),  # Purple
    ]
    
    UI_HEIGHT = 80
    COLOR_BUTTON_SIZE = 50
    BUTTON_MARGIN = 10
    
    BORDER_WIDTH = 2
    REGION_HOVER_ALPHA = 50