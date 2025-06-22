# Copyright (C) 2025 Bishoy Wadea
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import pygame
import math
from view.config import Config
from view.map_data import LEVELS

class Menu:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        # Larger, more playful fonts
        self.font_title = pygame.font.Font(None, 84)
        self.font_button = pygame.font.Font(None, 56)
        self.font_desc = pygame.font.Font(None, 42)
        self.font_small = pygame.font.Font(None, 36)
        
        # Menu states
        self.state = 'level_categories'  # 'level_categories', 'level_selection'
        self.selected_category = None
        self.selected_level = None
        
        # Buttons
        self.category_buttons = []
        self.level_buttons = []
        self.back_button = None

        # Animation variables for fun effects
        self.animation_time = 0
        self.star_positions = []
        self.generate_stars()
        
        self.setup_category_buttons()
        self.setup_back_button()

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
            if self.state == 'level_categories':
                for button in self.category_buttons:
                    button['hovered'] = button['rect'].collidepoint(mouse_pos)
            elif self.state == 'level_selection':
                # Check back button hover only on the level selection screen
                self.back_button['hovered'] = self.back_button['rect'].collidepoint(mouse_pos)
                for button in self.level_buttons:
                    button['hovered'] = button['rect'].collidepoint(mouse_pos)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check back button click (except on main menu)
                if self.state == 'level_selection' and self.back_button['rect'].collidepoint(mouse_pos):
                    self.state = 'level_categories'
                    return False
                
                if self.state == 'level_categories':
                    for button in self.category_buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            self.selected_category = button['tag']
                            self.setup_level_buttons(self.selected_category)
                            self.state = 'level_selection'
                
                elif self.state == 'level_selection':
                    for button in self.level_buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            self.selected_level = button['level']
                            return True # Return True to signal game start

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
        
        if self.state == 'level_categories':
            self.draw_category_menu(screen)
        elif self.state == 'level_selection':
            self.draw_level_selection(screen)
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