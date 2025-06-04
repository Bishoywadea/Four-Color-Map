import pygame

class GameManager:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode((800, 600))
        
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        
        # Set up font
        self.font = pygame.font.Font(None, 72)
        self.text = self.font.render("Four Color Map", True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(self.width // 2, self.height // 2))
        
    def handle_event(self, event):
        """Handle game events."""
        pass
    
    def update(self, dt):
        """Update game state."""
        pass
    
    def render(self):
        """Render the game."""
        # Clear screen with a nice background color
        self.screen.fill((30, 30, 40))
        
        # Draw the text
        self.screen.blit(self.text, self.text_rect)