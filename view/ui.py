import pygame
from view.config import Config

class Button:
    def __init__(self, x, y, width, height, color, text="", callback=None, icon_char=None, icon_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.callback = callback
        self.hovered = False
        self.icon_char = icon_char
        self.icon_path = icon_path
        self.icon_image = None
        
        # Load icon image if path is provided
        if self.icon_path:
            self.load_icon()
        
    def load_icon(self):
        """Load and scale the icon image."""
        try:
            # Load the PNG image
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            
            # Calculate icon size (leave some padding)
            icon_size = min(self.rect.width - 10, self.rect.height - 10)
            
            # Scale the image to fit the button
            self.icon_image = pygame.transform.scale(self.icon_image, (icon_size, icon_size))
            
        except pygame.error as e:
            print(f"Could not load icon {self.icon_path}: {e}")
            self.icon_image = None
            
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
        
        # Draw PNG icon if available
        if self.icon_image:
            icon_rect = self.icon_image.get_rect(center=self.rect.center)
            surface.blit(self.icon_image, icon_rect)
        # Fall back to character icon
        elif self.icon_char:
            font = pygame.font.Font(None, int(self.rect.height * 0.6))
            text_surface = font.render(self.icon_char, True, Config.COLORS['TEXT'])
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        # Fall back to text
        elif self.text:
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
        
        # Add color buttons
        for i, color in enumerate(Config.GAME_COLORS):
            button_x = Config.BUTTON_MARGIN + i * (Config.COLOR_BUTTON_SIZE + Config.BUTTON_MARGIN)
            button = Button(
                button_x, button_y,
                Config.COLOR_BUTTON_SIZE, Config.COLOR_BUTTON_SIZE,
                color,
                callback=lambda idx=i: self.select_color(idx)
            )
            self.color_buttons.append(button)
        
        # Add Eraser button (after color buttons)
        eraser_x = Config.BUTTON_MARGIN + len(Config.GAME_COLORS) * (Config.COLOR_BUTTON_SIZE + Config.BUTTON_MARGIN)
        self.eraser_button = Button(
            eraser_x, button_y,
            Config.COLOR_BUTTON_SIZE, Config.COLOR_BUTTON_SIZE,
            (255, 255, 255),  # White background
            "",  # No text
            callback=self.select_eraser,
            icon_path="assets/images/eraser.png"
        )
        
        # Action buttons on the right
        button_width = 80
        
        # Menu button
        menu_x = Config.SCREEN_WIDTH - button_width - Config.BUTTON_MARGIN
        self.menu_button = Button(
            menu_x, button_y,
            button_width, Config.COLOR_BUTTON_SIZE,
            Config.COLORS['UI_BACKGROUND'],
            "Menu",
            callback=self.game_manager.return_to_menu,
            icon_path="assets/images/menu.png"
        )
        
        # Reset button
        reset_x = menu_x - button_width - Config.BUTTON_MARGIN
        self.reset_button = Button(
            reset_x, button_y,
            button_width, Config.COLOR_BUTTON_SIZE,
            Config.COLORS['UI_BACKGROUND'],
            "Reset",
            callback=self.game_manager.reset_game,
            icon_path="assets/images/reset.png"
        )
        
        # Undo button
        undo_x = reset_x - button_width - Config.BUTTON_MARGIN
        self.undo_button = Button(
            undo_x, button_y,
            button_width, Config.COLOR_BUTTON_SIZE,
            Config.COLORS['UI_BACKGROUND'],
            "",
            callback=self.game_manager.undo_last_action,
            icon_path="assets/images/undo.png"
        )
    
    def select_color(self, color_index):
        """Select a color for painting regions."""
        self.game_manager.selected_color = color_index
        self.game_manager.eraser_mode = False
    
    def select_eraser(self):
        """Select eraser mode."""
        self.game_manager.eraser_mode = True
        self.game_manager.selected_color = -1  # -1 indicates eraser
    
    def handle_event(self, event):
        """Handle UI events."""
        # Handle color button events
        for button in self.color_buttons:
            if button.handle_event(event):
                return True
        
        # Handle eraser button
        if self.eraser_button.handle_event(event):
            return True
        
        # Handle action buttons
        if self.reset_button.handle_event(event):
            return True
        if self.menu_button.handle_event(event):
            return True
        if self.undo_button.handle_event(event):
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
            
            # Draw selection indicator for color buttons
            if not self.game_manager.eraser_mode and i == self.game_manager.selected_color:
                pygame.draw.rect(surface, Config.COLORS['BORDER'], button.rect, 4)
        
        # Draw eraser button
        self.eraser_button.draw(surface)
        
        # Draw selection indicator for eraser
        if self.game_manager.eraser_mode:
            pygame.draw.rect(surface, Config.COLORS['BORDER'], self.eraser_button.rect, 4)
        
        # Draw action buttons
        self.reset_button.draw(surface)
        self.undo_button.draw(surface)
        self.menu_button.draw(surface)
        
        # Draw timer
        self.draw_timer(surface)
    
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