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
import logging
from view.config import Config

# Configure logging
logger = logging.getLogger(__name__)


class Button:
    def __init__(self, x, y, width, height, color, text="",
                 callback=None, icon_char=None, icon_path=None):
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
            self.icon_image = pygame.transform.scale(
                self.icon_image, (icon_size, icon_size))

        except pygame.error as e:
            logger.error(f"Could not load icon {self.icon_path}: {e}")
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
            text_surface = font.render(
                self.icon_char, True, Config.COLORS['TEXT'])
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

    def handle_event(self, event):
        """Handle UI events."""
        return False

    def update(self, dt):
        """Update UI state."""
        pass  # Add any UI animations or updates here

    def draw(self, surface):
        """Draw minimal UI - just the timer at the bottom"""
        # Draw a small status bar at the bottom
        ui_height = 40
        # Draw timer
        self.draw_timer(surface, ui_height)

    def draw_timer(self, surface, ui_height):
        """Draw the game timer."""
        elapsed_time = self.game_manager.get_elapsed_time()
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        font = pygame.font.Font(None, 32)
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        text_surface = font.render(timer_text, True, Config.COLORS['TEXT'])

        # Position timer in the middle of status bar
        text_rect = text_surface.get_rect()
        text_rect.center = (Config.SCREEN_WIDTH // 2,
                            Config.SCREEN_HEIGHT - ui_height // 2 - 50)

        surface.blit(text_surface, text_rect)
