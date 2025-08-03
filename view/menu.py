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
from view.config import Config
from view.map_data import LEVELS


class Menu:
    def __init__(self, game_manager):
        self.game_manager = game_manager

        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 48)
        self.font_desc = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 32)

        self.state = 'level_categories'
        self.selected_category = None
        self.selected_level = None

        self.category_buttons = []
        self.level_buttons = []
        self.back_button = None

    def draw_button(self, screen, rect, color, border_color, text, font, text_color, hovered=False):
        if hovered:
            color = tuple(min(255, c + 30) for c in color)

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, border_color, rect, 3)

        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def setup_back_button(self, screen_width, screen_height):
        self.back_button = {
            'rect': pygame.Rect(50, screen_height - 100, 120, 50),
            'text': 'Back',
            'hovered': False
        }

    def setup_category_buttons(self, screen_width, screen_height):
        self.category_buttons = []
        button_width = 250
        button_height = 80
        button_spacing = 60

        categories = [
            {'name': 'Countries', 'color': (150, 255, 150)},
            {'name': 'Polygons', 'color': (255, 200, 100)}
        ]

        total_width = len(categories) * button_width + (len(categories) - 1) * button_spacing
        start_x = max((screen_width - total_width) // 2, 50)
        start_y = 350

        for i, category in enumerate(categories):
            self.category_buttons.append({
                'rect': pygame.Rect(
                    start_x + i * (button_width + button_spacing),
                    start_y,
                    button_width,
                    button_height
                ),
                'text': category['name'],
                'tag': category['name'].lower(),
                'hovered': False,
                'color': category['color']
            })

    def setup_level_buttons(self, category, screen_width, screen_height):
        self.level_buttons = []
        filtered_levels = [level for level in LEVELS if level.get('tag') == category]
        if not filtered_levels:
            return

        button_width = 400
        button_height = 70
        button_spacing = 20
        start_y = 320

        level_colors = [
            (255, 180, 180), (180, 255, 180),
            (180, 180, 255), (255, 255, 180),
            (255, 180, 255), (180, 255, 255),
        ]

        for i, level in enumerate(filtered_levels):
            button_y = start_y + i * (button_height + button_spacing)
            button_rect = pygame.Rect(
                (screen_width - button_width) // 2,
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

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            if self.state == 'level_categories':
                for button in self.category_buttons:
                    button['hovered'] = button['rect'].collidepoint(mouse_pos)
            elif self.state == 'level_selection':
                if self.back_button:
                    self.back_button['hovered'] = self.back_button['rect'].collidepoint(mouse_pos)
                for button in self.level_buttons:
                    button['hovered'] = button['rect'].collidepoint(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if self.state == 'level_selection' and self.back_button and self.back_button['rect'].collidepoint(mouse_pos):
                    self.state = 'level_categories'
                    return False

                if self.state == 'level_categories':
                    for button in self.category_buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            self.selected_category = button['tag']
                            self.setup_level_buttons(self.selected_category, pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height())
                            self.state = 'level_selection'

                elif self.state == 'level_selection':
                    for button in self.level_buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            self.selected_level = button['level']
                            return True

        return False

    def draw(self, screen):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        if not self.category_buttons:
            self.setup_category_buttons(screen_width, screen_height)
        if not self.back_button:
            self.setup_back_button(screen_width, screen_height)
        
        screen.fill((135, 206, 235))

        title_text = "Four Color Map Puzzle"
        title_surface = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen_width // 2, 160))
        bg_rect = title_rect.inflate(60, 40)
        pygame.draw.rect(screen, (50, 100, 200), bg_rect)
        screen.blit(title_surface, title_rect)

        if self.state == 'level_categories':
            self.draw_category_menu(screen)
        elif self.state == 'level_selection':
            self.draw_level_selection(screen)
            self.draw_back_button(screen)

    def draw_back_button(self, screen):
        if not self.back_button:
            return
        color = (100, 255, 100) if self.back_button['hovered'] else (150, 200, 255)
        self.draw_button(screen, self.back_button['rect'],
                         color, (100, 100, 100),
                         self.back_button['text'],
                         self.font_small, (50, 50, 50),
                         self.back_button['hovered'])

    def draw_category_menu(self, screen):
        screen_width = screen.get_width()
        
        subtitle_text = "Pick Your Map Adventure!"
        subtitle_surface = self.font_desc.render(subtitle_text, True, (255, 255, 255))
        subtitle_rect = subtitle_surface.get_rect(center=(screen_width // 2, 240))
        bg_rect = subtitle_rect.inflate(40, 20)
        pygame.draw.rect(screen, (255, 150, 100), bg_rect)
        screen.blit(subtitle_surface, subtitle_rect)

        for button in self.category_buttons:
            self.draw_button(screen, button['rect'],
                             button['color'], (100, 100, 100),
                             button['text'], self.font_button,
                             (50, 50, 50), button['hovered'])

    def draw_level_selection(self, screen):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        category_name = self.selected_category.capitalize()
        subtitle_text = f"Choose Your {category_name} Challenge!"
        subtitle_surface = self.font_desc.render(subtitle_text, True, (255, 255, 255))
        subtitle_rect = subtitle_surface.get_rect(center=(screen_width // 2, 240))
        bg_rect = subtitle_rect.inflate(40, 20)
        pygame.draw.rect(screen, (150, 255, 150), bg_rect)
        screen.blit(subtitle_surface, subtitle_rect)

        if not self.level_buttons:
            no_levels_text = f"No {category_name} maps available yet!"
            no_levels_surface = self.font_desc.render(no_levels_text, True, (255, 100, 100))
            no_levels_rect = no_levels_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(no_levels_surface, no_levels_rect)
        else:
            for button in self.level_buttons:
                self.draw_button(screen, button['rect'],
                                 button['color'], (100, 100, 100),
                                 "", self.font_button,
                                 (50, 50, 50), button['hovered'])

                level_name = button['level']['name']
                level_surface = self.font_button.render(level_name, True, (50, 50, 50))
                level_rect = level_surface.get_rect(center=(button['rect'].centerx, button['rect'].centery - 10))
                screen.blit(level_surface, level_rect)

                desc_surface = self.font_small.render(button['level']['description'], True, (80, 80, 80))
                desc_rect = desc_surface.get_rect(center=(button['rect'].centerx, button['rect'].centery + 15))
                screen.blit(desc_surface, desc_rect)
