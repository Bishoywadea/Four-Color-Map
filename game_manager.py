import pygame
from config import Config
from menu import Menu

class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        screen_info = pygame.display.Info()
        Config.SCREEN_WIDTH = screen_info.current_w
        Config.SCREEN_HEIGHT = screen_info.current_h
        
        pygame.display.set_caption("Four Color Map Puzzle")
        
        # Game states
        self.STATE_MENU = "menu"
        self.STATE_PLAYING = "playing"
        self.current_state = self.STATE_MENU
        
        # Menu
        self.menu = Menu(self)
        
    
    def handle_event(self, event):
        """Handle game events."""
        if self.current_state == self.STATE_MENU:
            if self.menu.handle_event(event):
                # Level was selected
                self.start_level(self.menu.selected_level)
                
    
    def update(self, dt):
        """Update game state."""
        pass
    
    def render(self):
        """Render the game."""
        if self.current_state == self.STATE_MENU:
            self.menu.draw(self.screen)