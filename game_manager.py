import pygame

class GameManager:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode((800, 600))
        
        self.font = pygame.font.Font(None, 72)
        self.text = self.font.render("Four Color Map", True, (255, 255, 255))
        
        self.update_text_position()
        
    def update_text_position(self):
        """Update text position based on current screen size"""
        if self.screen:
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
            self.text_rect = self.text.get_rect(center=(self.width // 2, self.height // 2))
    
    def handle_event(self, event):
        """Handle game events."""
        if event.type == pygame.VIDEORESIZE:
            self.update_text_position()
    
    def update(self, dt):
        """Update game state."""
        pass
    
    def render(self):
        """Render the game."""
        self.update_text_position()
        
        self.screen.fill((30, 30, 40))
        
        self.screen.blit(self.text, self.text_rect)