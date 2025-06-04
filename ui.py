import pygame
from config import Config

class Button:
    def __init__(self, x, y, width, height, color, text="", callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.callback = callback
        self.hovered = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False
    
    def draw(self, surface):
        color = Config.COLORS['BUTTON_HOVER'] if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, Config.COLORS['BORDER'], self.rect, 2)
        
        if self.text:
            font = pygame.font.Font(None, 24)
            text_surface = font.render(self.text, True, Config.COLORS['TEXT'])
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

class UI:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.color_buttons = []
        self.setup_ui()
        
    def setup_ui(self):
        """Set up UI elements."""
        # Create color selection buttons
        button_y = Config.SCREEN_HEIGHT - Config.UI_HEIGHT + Config.BUTTON_MARGIN
        
        for i, color in enumerate(Config.GAME_COLORS):
            button_x = Config.BUTTON_MARGIN + i * (Config.COLOR_BUTTON_SIZE + Config.BUTTON_MARGIN)
            button = Button(
                button_x, button_y,
                Config.COLOR_BUTTON_SIZE, Config.COLOR_BUTTON_SIZE,
                color,
                callback=lambda idx=i: self.select_color(idx)
            )
            self.color_buttons.append(button)
        
        # Reset button
        reset_x = Config.SCREEN_WIDTH - 100 - Config.BUTTON_MARGIN
        self.reset_button = Button(
            reset_x, button_y,
            100, Config.COLOR_BUTTON_SIZE,
            Config.COLORS['UI_BACKGROUND'],
            "Reset",
            callback=self.game_manager.reset_game
        )
        menu_x = reset_x - 120
        self.menu_button = Button(
            menu_x, button_y,
            100, Config.COLOR_BUTTON_SIZE,
            Config.COLORS['UI_BACKGROUND'],
            "Menu",
            callback=self.game_manager.return_to_menu
        )
    
    def select_color(self, color_index):
        """Select a color for painting regions."""
        self.game_manager.selected_color = color_index
    
    def handle_event(self, event):
        """Handle UI events."""
        # Handle color button events
        for button in self.color_buttons:
            if button.handle_event(event):
                return True
        
        # Handle reset button event
        if self.reset_button.handle_event(event):
            return True
        if self.menu_button.handle_event(event):
            return True
        
        return False
    
    def update(self, dt):
        """Update UI state."""
        pass  # Add any UI animations or updates here
    
    def draw(self, surface):
        """Draw the UI."""
        # Draw UI background
        ui_rect = pygame.Rect(0, Config.SCREEN_HEIGHT - Config.UI_HEIGHT, 
                            Config.SCREEN_WIDTH, Config.UI_HEIGHT)
        pygame.draw.rect(surface, Config.COLORS['UI_BACKGROUND'], ui_rect)
        pygame.draw.rect(surface, Config.COLORS['BORDER'], ui_rect, 2)
        
        # Draw color buttons
        for i, button in enumerate(self.color_buttons):
            button.draw(surface)
            
            # Draw selection indicator
            if i == self.game_manager.selected_color:
                pygame.draw.rect(surface, Config.COLORS['BORDER'], button.rect, 4)
        
        # Draw reset button
        self.reset_button.draw(surface)
        
        # Draw timer
        self.draw_timer(surface)
        
        # Draw instructions
        self.menu_button.draw(surface)

    
    def draw_timer(self, surface):
        """Draw the game timer."""
        elapsed_time = self.game_manager.get_elapsed_time()
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        font = pygame.font.Font(None, 36)
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        text_surface = font.render(timer_text, True, Config.COLORS['TEXT'])
        
        # Position timer in the middle of UI area
        text_rect = text_surface.get_rect()
        text_rect.center = (Config.SCREEN_WIDTH // 2, 
                          Config.SCREEN_HEIGHT - Config.UI_HEIGHT // 2)
        
        surface.blit(text_surface, text_rect)