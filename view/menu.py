# menu.py
import pygame
from view.config import Config
from view.map_data import LEVELS

class Menu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 48)
        self.font_desc = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 28)
        
        # Menu states
        self.state = 'main'  # 'main', 'level_categories', 'level_selection'
        self.selected_category = None
        self.selected_level = None
        
        # Buttons
        self.main_buttons = []
        self.category_buttons = []
        self.level_buttons = []
        self.back_button = None
        
        self.setup_main_buttons()
        self.setup_category_buttons()
        self.setup_back_button()
        
    def setup_back_button(self):
        """Set up the back button."""
        button_width = 100
        button_height = 40
        self.back_button = {
            'rect': pygame.Rect(
                20,  # Left margin
                Config.SCREEN_HEIGHT - 60,  # Bottom position
                button_width,
                button_height
            ),
            'text': '← Back',
            'hovered': False
        }
        
    def setup_main_buttons(self):
        """Set up main menu buttons."""
        button_width = 300
        button_height = 80
        button_spacing = 30
        
        # Center buttons
        start_y = Config.SCREEN_HEIGHT // 2 - button_height - button_spacing // 2
        
        # Choose Level button
        self.main_buttons.append({
            'rect': pygame.Rect(
                (Config.SCREEN_WIDTH - button_width) // 2,
                start_y,
                button_width,
                button_height
            ),
            'text': 'Choose Level',
            'action': 'level_categories',
            'hovered': False
        })
        
        # Settings button
        self.main_buttons.append({
            'rect': pygame.Rect(
                (Config.SCREEN_WIDTH - button_width) // 2,
                start_y + button_height + button_spacing,
                button_width,
                button_height
            ),
            'text': 'Settings',
            'action': 'settings',
            'hovered': False
        })
    
    def setup_category_buttons(self):
        """Set up level category buttons."""
        button_width = 250
        button_height = 80
        button_spacing = 30
        
        categories = ['Countries', 'Polygons', 'Random']
        
        # Calculate starting position
        total_width = len(categories) * button_width + (len(categories) - 1) * button_spacing
        start_x = (Config.SCREEN_WIDTH - total_width) // 2
        start_y = Config.SCREEN_HEIGHT // 2 - button_height // 2
        
        for i, category in enumerate(categories):
            self.category_buttons.append({
                'rect': pygame.Rect(
                    start_x + i * (button_width + button_spacing),
                    start_y,
                    button_width,
                    button_height
                ),
                'text': category,
                'tag': category.lower(),
                'hovered': False
            })
    
    def setup_level_buttons(self, category):
        """Set up level selection buttons for a specific category."""
        self.level_buttons = []
        
        # Filter levels by category tag
        filtered_levels = [level for level in LEVELS if level.get('tag') == category]
        
        if not filtered_levels:
            return
        
        button_width = 400
        button_height = 80
        button_spacing = 20
        
        # Calculate starting Y position
        total_height = len(filtered_levels) * (button_height + button_spacing) - button_spacing
        start_y = (Config.SCREEN_HEIGHT - total_height) // 2 + 50
        
        for i, level in enumerate(filtered_levels):
            button_y = start_y + i * (button_height + button_spacing)
            button_rect = pygame.Rect(
                (Config.SCREEN_WIDTH - button_width) // 2,
                button_y,
                button_width,
                button_height
            )
            
            self.level_buttons.append({
                'rect': button_rect,
                'level': level,
                'hovered': False
            })
    
    def handle_event(self, event):
        """Handle menu events."""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            # Check back button hover (except on main menu)
            if self.state != 'main':
                self.back_button['hovered'] = self.back_button['rect'].collidepoint(mouse_pos)
            
            if self.state == 'main':
                for button in self.main_buttons:
                    button['hovered'] = button['rect'].collidepoint(mouse_pos)
            elif self.state == 'level_categories':
                for button in self.category_buttons:
                    button['hovered'] = button['rect'].collidepoint(mouse_pos)
            elif self.state == 'level_selection':
                for button in self.level_buttons:
                    button['hovered'] = button['rect'].collidepoint(mouse_pos)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check back button click (except on main menu)
                if self.state != 'main' and self.back_button['rect'].collidepoint(mouse_pos):
                    if self.state == 'level_selection':
                        self.state = 'level_categories'
                    elif self.state == 'level_categories':
                        self.state = 'main'
                    return False
                
                if self.state == 'main':
                    for button in self.main_buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            if button['action'] == 'level_categories':
                                self.state = 'level_categories'
                            elif button['action'] == 'settings':
                                # Settings does nothing for now
                                pass
                
                elif self.state == 'level_categories':
                    for button in self.category_buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            self.selected_category = button['tag']
                            self.setup_level_buttons(self.selected_category)
                            self.state = 'level_selection'
                
                elif self.state == 'level_selection':
                    for button in self.level_buttons:
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
        
        if self.state == 'main':
            self.draw_main_menu(screen)
        elif self.state == 'level_categories':
            self.draw_category_menu(screen)
        elif self.state == 'level_selection':
            self.draw_level_selection(screen)
        
        # Draw back button (except on main menu)
        if self.state != 'main':
            self.draw_back_button(screen)
    
    def draw_back_button(self, screen):
        """Draw the back button."""
        color = Config.COLORS['BUTTON_HOVER'] if self.back_button['hovered'] else Config.COLORS['UI_BACKGROUND']
        pygame.draw.rect(screen, color, self.back_button['rect'])
        pygame.draw.rect(screen, Config.COLORS['BORDER'], self.back_button['rect'], 2)
        
        text = self.font_small.render(self.back_button['text'], True, Config.COLORS['TEXT'])
        text_rect = text.get_rect(center=self.back_button['rect'].center)
        screen.blit(text, text_rect)
    
    def draw_main_menu(self, screen):
        """Draw the main menu."""
        # Draw subtitle
        subtitle_text = self.font_desc.render("Main Menu", True, Config.COLORS['TEXT'])
        subtitle_rect = subtitle_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 150))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        for button in self.main_buttons:
            color = Config.COLORS['BUTTON_HOVER'] if button['hovered'] else Config.COLORS['UI_BACKGROUND']
            pygame.draw.rect(screen, color, button['rect'])
            pygame.draw.rect(screen, Config.COLORS['BORDER'], button['rect'], 3)
            
            text = self.font_button.render(button['text'], True, Config.COLORS['TEXT'])
            text_rect = text.get_rect(center=button['rect'].center)
            screen.blit(text, text_rect)
    
    def draw_category_menu(self, screen):
        """Draw the category selection menu."""
        # Draw subtitle
        subtitle_text = self.font_desc.render("Select Map Category", True, Config.COLORS['TEXT'])
        subtitle_rect = subtitle_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 150))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw category buttons
        for button in self.category_buttons:
            color = Config.COLORS['BUTTON_HOVER'] if button['hovered'] else Config.COLORS['UI_BACKGROUND']
            pygame.draw.rect(screen, color, button['rect'])
            pygame.draw.rect(screen, Config.COLORS['BORDER'], button['rect'], 3)
            
            text = self.font_button.render(button['text'], True, Config.COLORS['TEXT'])
            text_rect = text.get_rect(center=button['rect'].center)
            screen.blit(text, text_rect)
    
    def draw_level_selection(self, screen):
        """Draw the level selection menu."""
        # Draw subtitle
        category_name = self.selected_category.capitalize()
        subtitle_text = self.font_desc.render(f"Select {category_name} Map", True, Config.COLORS['TEXT'])
        subtitle_rect = subtitle_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 150))
        screen.blit(subtitle_text, subtitle_rect)
        
        if not self.level_buttons:
            # No levels found message
            no_levels_text = self.font_desc.render(f"No {category_name} maps available", True, Config.COLORS['TEXT'])
            no_levels_rect = no_levels_text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
            screen.blit(no_levels_text, no_levels_rect)
        else:
            # Draw level buttons
            for button in self.level_buttons:
                # Button background
                color = Config.COLORS['BUTTON_HOVER'] if button['hovered'] else Config.COLORS['UI_BACKGROUND']
                pygame.draw.rect(screen, color, button['rect'])
                pygame.draw.rect(screen, Config.COLORS['BORDER'], button['rect'], 3)
                
                # Level name
                level_text = self.font_button.render(button['level']['name'], True, Config.COLORS['TEXT'])
                level_rect = level_text.get_rect(center=(button['rect'].centerx, button['rect'].centery - 10))
                screen.blit(level_text, level_rect)
                
                # Level description
                desc_text = self.font_small.render(button['level']['description'], True, Config.COLORS['TEXT'])
                desc_rect = desc_text.get_rect(center=(button['rect'].centerx, button['rect'].centery + 15))
                screen.blit(desc_text, desc_rect)