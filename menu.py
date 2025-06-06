import pygame
from config import Config
from map_data import LEVELS

class Menu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 48)
        self.font_desc = pygame.font.Font(None, 32)
        self.buttons = []
        self.selected_level = None
        self.setup_buttons()
        
    def setup_buttons(self):
        """Set up level selection buttons."""
        button_width = 400
        button_height = 100
        button_spacing = 20
        
        # Calculate starting Y position
        total_height = len(LEVELS) * (button_height + button_spacing) - button_spacing
        start_y = (Config.SCREEN_HEIGHT - total_height) // 2 + 50
        
        for i, level in enumerate(LEVELS):
            button_y = start_y + i * (button_height + button_spacing)
            button_rect = pygame.Rect(
                (Config.SCREEN_WIDTH - button_width) // 2,
                button_y,
                button_width,
                button_height
            )
            
            self.buttons.append({
                'rect': button_rect,
                'level': level,
                'hovered': False
            })
    
    def handle_event(self, event):
        """Handle menu events."""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            for button in self.buttons:
                button['hovered'] = button['rect'].collidepoint(mouse_pos)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                for button in self.buttons:
                    if button['rect'].collidepoint(mouse_pos):
                        self.selected_level = button['level']
                        return True
        
        return False
    
    def draw(self, screen):
        """Draw the menu."""
        # Clear screen
        screen.fill(Config.COLORS['BACKGROUND'])
        
        # Draw title
        title_text = self.font_title.render("Four Color Map Puzzle", True, Config.COLORS['TEXT'])
        title_rect = title_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 80))
        
        # Title background
        title_bg = title_rect.inflate(40, 20)
        pygame.draw.rect(screen, Config.COLORS['UI_BACKGROUND'], title_bg)
        pygame.draw.rect(screen, Config.COLORS['BORDER'], title_bg, 3)
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.font_desc.render("Select a Level", True, Config.COLORS['TEXT'])
        subtitle_rect = subtitle_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 150))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw level buttons
        for button in self.buttons:
            # Button background
            color = Config.COLORS['BUTTON_HOVER'] if button['hovered'] else Config.COLORS['UI_BACKGROUND']
            pygame.draw.rect(screen, color, button['rect'])
            pygame.draw.rect(screen, Config.COLORS['BORDER'], button['rect'], 3)
            
            # Level name
            level_text = self.font_button.render(button['level']['name'], True, Config.COLORS['TEXT'])
            level_rect = level_text.get_rect(center=(button['rect'].centerx, button['rect'].centery - 15))
            screen.blit(level_text, level_rect)
            
            # Level description
            desc_text = self.font_desc.render(button['level']['description'], True, Config.COLORS['TEXT'])
            desc_rect = desc_text.get_rect(center=(button['rect'].centerx, button['rect'].centery + 20))
            screen.blit(desc_text, desc_rect)
        
        # Draw instructions
        inst_text = self.font_desc.render("Click a level to start playing", True, Config.COLORS['TEXT'])
        inst_rect = inst_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT - 50))
        screen.blit(inst_text, inst_rect)