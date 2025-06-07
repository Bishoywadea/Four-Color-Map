import pygame
import math
from view.config import Config
from view.map_data import LEVELS
from view.color_picker import SimpleColorPicker

class Menu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        # Larger, more playful fonts
        self.font_title = pygame.font.Font(None, 84)
        self.font_button = pygame.font.Font(None, 56)
        self.font_desc = pygame.font.Font(None, 42)
        self.font_small = pygame.font.Font(None, 36)
        
        # Menu states
        self.state = 'main'  # 'main', 'level_categories', 'level_selection'
        self.selected_category = None
        self.selected_level = None
        
        # Buttons
        self.main_buttons = []
        self.category_buttons = []
        self.level_buttons = []
        self.back_button = None

        # Settings components
        self.color_previews = []
        self.color_picker = None
        self.reset_colors_button = None
        self.selected_color_index = None
        
        # Animation variables for fun effects
        self.animation_time = 0
        self.star_positions = []
        self.generate_stars()
        
        self.setup_main_buttons()
        self.setup_category_buttons()
        self.setup_back_button()
        self.setup_settings_components()

    def generate_stars(self):
        """Generate random star positions for background decoration."""
        import random
        self.star_positions = []
        for _ in range(20):
            x = random.randint(50, Config.SCREEN_WIDTH - 50)
            y = random.randint(50, Config.SCREEN_HEIGHT - 50)
            size = random.randint(2, 6)
            self.star_positions.append((x, y, size))

    def draw_star(self, screen, x, y, size, color=(255, 255, 100)):
        """Draw a cute star shape."""
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                # Outer points
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
            else:
                # Inner points
                px = x + (size * 0.4) * math.cos(angle)
                py = y + (size * 0.4) * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(screen, color, points)

    def draw_colorful_border(self, screen, rect, thickness=3):
        """Draw a colorful border around a rectangle."""
        # Use alternating bright colors instead of rainbow
        colors = [
            (100, 200, 255),  # Bright blue
            (255, 100, 150),  # Bright pink
            (100, 255, 150),  # Bright green
        ]
        
        for i in range(thickness):
            color = colors[i % len(colors)]
            pygame.draw.rect(screen, color, rect.inflate(i*2, i*2), 1)

    def draw_button_with_shadow(self, screen, rect, color, border_color, text, font, text_color, hovered=False):
        """Draw a button with shadow and fun styling."""
        # Shadow
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=15)
        
        # Main button with rounded corners
        button_color = color
        if hovered:
            button_color = tuple(min(255, c + 30) for c in color)
        
        pygame.draw.rect(screen, button_color, rect, border_radius=15)
        
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=15)
        
        # Button text
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def setup_settings_components(self):
        """Set up settings menu components."""
        # Create color previews - larger and more spaced out
        preview_size = 120
        preview_spacing = 50
        start_x = Config.SCREEN_WIDTH // 2 - (2 * preview_size + 1.5 * preview_spacing)
        start_y = 280
        
        for i in range(4):
            x = start_x + i * (preview_size + preview_spacing)
            preview_rect = pygame.Rect(x, start_y, preview_size, preview_size)
            self.color_previews.append({
                'rect': preview_rect,
                'index': i,
                'selected': False
            })
        
        # Create color picker
        picker_x = (Config.SCREEN_WIDTH - 265) // 2
        picker_y = start_y + preview_size + 100
        self.color_picker = SimpleColorPicker(picker_x, picker_y)
        
        # Reset colors button - larger and more colorful
        button_width = 250
        button_height = 70
        self.reset_colors_button = {
            'rect': pygame.Rect(
                (Config.SCREEN_WIDTH - button_width) // 2,
                picker_y + 300,
                button_width,
                button_height
            ),
            'text': 'Reset Colors',
            'hovered': False
        }
        
    def setup_back_button(self):
        """Set up the back button."""
        button_width = 120
        button_height = 50
        self.back_button = {
            'rect': pygame.Rect(
                30,  # Left margin
                Config.SCREEN_HEIGHT - 80,  # Bottom position
                button_width,
                button_height
            ),
            'text': 'Back',
            'hovered': False
        }
        
    def setup_main_buttons(self):
        """Set up main menu buttons."""
        button_width = 350
        button_height = 90
        button_spacing = 40
        
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
            'text': 'Choose Adventure',
            'action': 'level_categories',
            'hovered': False,
            'color': (100, 200, 255)  # Light blue
        })
        
        # Settings button
        self.main_buttons.append({
            'rect': pygame.Rect(
                (Config.SCREEN_WIDTH - button_width) // 2,
                start_y + button_height + button_spacing,
                button_width,
                button_height
            ),
            'text': 'Color Settings',
            'action': 'settings',
            'hovered': False,
            'color': (255, 150, 200)  # Light pink
        })
    
    def setup_category_buttons(self):
        """Set up level category buttons."""
        button_width = 280
        button_height = 100
        button_spacing = 50
        
        categories = [
            {'name': 'Countries', 'color': (150, 255, 150)},
            {'name': 'Polygons', 'color': (255, 200, 100)}
        ]
        
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
                'text': f"{category['name']}",
                'tag': category['name'].lower(),
                'hovered': False,
                'color': category['color']
            })
    
    def setup_level_buttons(self, category):
        """Set up level selection buttons for a specific category."""
        self.level_buttons = []
        
        # Filter levels by category tag
        filtered_levels = [level for level in LEVELS if level.get('tag') == category]
        
        if not filtered_levels:
            return
        
        button_width = 450
        button_height = 90
        button_spacing = 25
        
        # Calculate starting Y position
        total_height = len(filtered_levels) * (button_height + button_spacing) - button_spacing
        start_y = (Config.SCREEN_HEIGHT - total_height) // 2 + 60
        
        # Fun colors for level buttons
        level_colors = [
            (255, 180, 180),  # Light red
            (180, 255, 180),  # Light green
            (180, 180, 255),  # Light blue
            (255, 255, 180),  # Light yellow
            (255, 180, 255),  # Light magenta
            (180, 255, 255),  # Light cyan
        ]
        
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
                'hovered': False,
                'color': level_colors[i % len(level_colors)]
            })
    
    def update_animation(self):
        """Update animation variables."""
        self.animation_time += 0.02
    
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
            elif self.state == 'settings':
                self.reset_colors_button['hovered'] = self.reset_colors_button['rect'].collidepoint(mouse_pos)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check back button click (except on main menu)
                if self.state != 'main' and self.back_button['rect'].collidepoint(mouse_pos):
                    if self.state == 'level_selection':
                        self.state = 'level_categories'
                    elif self.state == 'level_categories':
                        self.state = 'main'
                    elif self.state == 'settings':
                        self.state = 'main'
                        # Reset selected states when leaving settings
                        self.selected_color_index = None
                        for preview in self.color_previews:
                            preview['selected'] = False
                    return False
                
                if self.state == 'main':
                    for button in self.main_buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            if button['action'] == 'level_categories':
                                self.state = 'level_categories'
                            elif button['action'] == 'settings':
                                self.state = 'settings'
                
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
                
                elif self.state == 'settings':
                    # Check color preview clicks
                    for preview in self.color_previews:
                        if preview['rect'].collidepoint(mouse_pos):
                            # Deselect all previews
                            for p in self.color_previews:
                                p['selected'] = False
                            # Select this one
                            preview['selected'] = True
                            self.selected_color_index = preview['index']
                            # Set color picker to current color
                            self.color_picker.selected_color = Config.GAME_COLORS[preview['index']]
                    
                    # Check color picker clicks
                    if self.color_picker.handle_event(event):
                        if self.selected_color_index is not None and self.color_picker.selected_color:
                            Config.GAME_COLORS[self.selected_color_index] = self.color_picker.selected_color
                    
                    # Check reset button
                    if self.reset_colors_button['rect'].collidepoint(mouse_pos):
                        Config.reset_colors()
                        # Clear selections
                        self.selected_color_index = None
                        for preview in self.color_previews:
                            preview['selected'] = False
        
        return False
    
    def draw(self, screen):
        """Draw the menu."""
        # Update animations
        self.update_animation()
        
        # Gradient background
        self.draw_gradient_background(screen)
        
        # Draw animated stars
        self.draw_animated_stars(screen)
        
        # Draw title with fun effects
        self.draw_fancy_title(screen)
        
        if self.state == 'main':
            self.draw_main_menu(screen)
        elif self.state == 'level_categories':
            self.draw_category_menu(screen)
        elif self.state == 'level_selection':
            self.draw_level_selection(screen)
        elif self.state == 'settings':
            self.draw_settings_menu(screen)
        
        # Draw back button (except on main menu)
        if self.state != 'main':
            self.draw_back_button(screen)

    def draw_gradient_background(self, screen):
        """Draw a colorful gradient background."""
        # Create a simple vertical gradient
        for y in range(Config.SCREEN_HEIGHT):
            ratio = y / Config.SCREEN_HEIGHT
            r = int(135 + (200 - 135) * ratio)  # Light blue to light purple
            g = int(206 + (150 - 206) * ratio)
            b = int(235 + (255 - 235) * ratio)
            color = (r, g, b)
            pygame.draw.line(screen, color, (0, y), (Config.SCREEN_WIDTH, y))

    def draw_animated_stars(self, screen):
        """Draw twinkling stars in the background."""
        for i, (x, y, size) in enumerate(self.star_positions):
            # Make stars twinkle
            alpha = abs(math.sin(self.animation_time * 2 + i)) * 0.5 + 0.5
            brightness = int(255 * alpha)
            color = (brightness, brightness, 100)
            self.draw_star(screen, x, y, size, color)

    def draw_fancy_title(self, screen):
        """Draw the title with fun effects."""
        title_text = "Four Color Map Puzzle"
        
        # Create title surface with larger font
        title_surface = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 80))
        
        # Animated background
        bg_rect = title_rect.inflate(60, 40)
        # Pulsing effect
        pulse = abs(math.sin(self.animation_time * 3)) * 20 + 10
        bg_color = (50 + pulse, 100 + pulse, 200 + pulse)
        pygame.draw.rect(screen, bg_color, bg_rect, border_radius=20)
        
        # Shadow text
        shadow_surface = self.font_title.render(title_text, True, (50, 50, 50))
        shadow_rect = shadow_surface.get_rect(center=(title_rect.centerx + 3, title_rect.centery + 3))
        screen.blit(shadow_surface, shadow_rect)
        
        # Main title
        screen.blit(title_surface, title_rect)
    
    def draw_back_button(self, screen):
        """Draw the back button."""
        color = (100, 255, 100) if self.back_button['hovered'] else (150, 200, 255)
        self.draw_button_with_shadow(screen, self.back_button['rect'], color, (100, 100, 100), 
                                   self.back_button['text'], self.font_small, (50, 50, 50), 
                                   self.back_button['hovered'])
    
    def draw_main_menu(self, screen):
        """Draw the main menu."""
        # Draw subtitle with fun styling
        subtitle_text = "Welcome! Choose Your Fun!"
        subtitle_surface = self.font_desc.render(subtitle_text, True, (255, 255, 255))
        subtitle_rect = subtitle_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 180))
        
        # Subtitle background
        bg_rect = subtitle_rect.inflate(40, 20)
        pygame.draw.rect(screen, (100, 150, 255, 128), bg_rect, border_radius=15)
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw buttons with fun colors
        for button in self.main_buttons:
            self.draw_button_with_shadow(screen, button['rect'], button['color'], (100, 100, 100),
                                       button['text'], self.font_button, (50, 50, 50), button['hovered'])
    
    def draw_category_menu(self, screen):
        """Draw the category selection menu."""
        # Draw subtitle
        subtitle_text = "Pick Your Map Adventure!"
        subtitle_surface = self.font_desc.render(subtitle_text, True, (255, 255, 255))
        subtitle_rect = subtitle_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 180))
        
        # Subtitle background
        bg_rect = subtitle_rect.inflate(40, 20)
        pygame.draw.rect(screen, (255, 150, 100, 128), bg_rect, border_radius=15)
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw category buttons
        for button in self.category_buttons:
            self.draw_button_with_shadow(screen, button['rect'], button['color'], (100, 100, 100),
                                       button['text'], self.font_button, (50, 50, 50), button['hovered'])
    
    def draw_level_selection(self, screen):
        """Draw the level selection menu."""
        # Draw subtitle
        category_name = self.selected_category.capitalize()
        subtitle_text = f"Choose Your {category_name} Challenge!"
        subtitle_surface = self.font_desc.render(subtitle_text, True, (255, 255, 255))
        subtitle_rect = subtitle_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 180))
        
        # Subtitle background
        bg_rect = subtitle_rect.inflate(40, 20)
        pygame.draw.rect(screen, (150, 255, 150, 128), bg_rect, border_radius=15)
        screen.blit(subtitle_surface, subtitle_rect)
        
        if not self.level_buttons:
            # No levels found message
            no_levels_text = f"No {category_name} maps available yet!"
            no_levels_surface = self.font_desc.render(no_levels_text, True, (255, 100, 100))
            no_levels_rect = no_levels_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
            screen.blit(no_levels_surface, no_levels_rect)
        else:
            # Draw level buttons
            for button in self.level_buttons:
                # Button with shadow and fun styling
                self.draw_button_with_shadow(screen, button['rect'], button['color'], (100, 100, 100),
                                           "", self.font_button, (50, 50, 50), button['hovered'])
                
                # Custom text layout for levels
                level_name = f"{button['level']['name']}"
                level_surface = self.font_button.render(level_name, True, (50, 50, 50))
                level_rect = level_surface.get_rect(center=(button['rect'].centerx, button['rect'].centery - 15))
                screen.blit(level_surface, level_rect)
                
                # Level description
                desc_surface = self.font_small.render(button['level']['description'], True, (80, 80, 80))
                desc_rect = desc_surface.get_rect(center=(button['rect'].centerx, button['rect'].centery + 20))
                screen.blit(desc_surface, desc_rect)

    def draw_settings_menu(self, screen):
        """Draw the settings menu."""
        # Draw subtitle
        subtitle_text = "Make It Your Colors!"
        subtitle_surface = self.font_desc.render(subtitle_text, True, (255, 255, 255))
        subtitle_rect = subtitle_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 180))
        
        # Subtitle background
        bg_rect = subtitle_rect.inflate(40, 20)
        pygame.draw.rect(screen, (255, 150, 255, 128), bg_rect, border_radius=15)
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Instructions with fun styling
        instruction_text = "Click a color box, then pick a new color!"
        instruction_surface = self.font_small.render(instruction_text, True, (255, 255, 255))
        instruction_rect = instruction_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 230))
        screen.blit(instruction_surface, instruction_rect)
        
        # Draw color previews with fun styling
        for i, preview in enumerate(self.color_previews):
            # Shadow for color box
            shadow_rect = preview['rect'].copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=15)
            
            # Draw the color box with rounded corners
            pygame.draw.rect(screen, Config.GAME_COLORS[i], preview['rect'], border_radius=15)
            
            # Draw border (colorful if selected, regular if not)
            if preview['selected']:
                self.draw_colorful_border(screen, preview['rect'], 4)
            else:
                pygame.draw.rect(screen, (100, 100, 100), preview['rect'], 3, border_radius=15)
            
            # Draw simple label above
            label_text = f"Color {i + 1}"
            label_surface = self.font_small.render(label_text, True, (255, 255, 255))
            label_rect = label_surface.get_rect(center=(preview['rect'].centerx, preview['rect'].top - 30))
            screen.blit(label_surface, label_rect)
        
        # Draw color picker
        self.color_picker.draw(screen)
        
        # Draw reset button with fun styling
        color = (255, 200, 100) if self.reset_colors_button['hovered'] else (200, 150, 255)
        self.draw_button_with_shadow(screen, self.reset_colors_button['rect'], color, (100, 100, 100),
                                   self.reset_colors_button['text'], self.font_button, (50, 50, 50),
                                   self.reset_colors_button['hovered'])