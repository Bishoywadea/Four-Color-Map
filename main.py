# This file is part of the Four Color Map game.
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
import sys
from logic.game_manager import GameManager
from view.config import Config
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gettext import gettext as _

class main:
    def __init__(self, journal=True):
        self.journal = journal
        self.running = True
        self.canvas = None
        self.score = [0, 0]
        self.show_help = False
        self.show_color_warning = False
        self.game = None
        self.question_text = None 
        self.close_text = None 
        self.warning_text = None 
        self.help_text = None 
        self.activity = None

    def set_activity(self, activity):
        """Set reference to the activity."""
        self.activity = activity
        if self.game:
            self.game.set_activity(activity)

    def toggle_help(self):
        """Toggle help display"""
        self.show_help = not self.show_help

    def set_canvas(self, canvas):
        self.canvas = canvas
        pygame.display.set_caption(_("Four Color Map Puzzle"))

    def write_file(self, file_path):
        pass

    def read_file(self, file_path):
        pass

    def quit(self):
        self.running = False
    
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode(event.size, pygame.RESIZABLE)
                break
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.show_color_warning:
                    self.show_color_warning = False
                elif self.show_help:
                    self.show_help = False
                else:
                    # Pass event to game manager
                    if self.game:
                        self.game.handle_event(event)
            else:
                # Pass other events to game manager
                if self.game:
                    self.game.handle_event(event)
    
    def draw_help(self, screen):
        if self.show_help:
            # Calculate size based on text
            padding = 20
            spacing = 10
            total_height = sum(text.get_height() + spacing for text in self.help_text) + padding * 2
            max_width = max(text.get_width() for text in self.help_text) + padding * 2
            
            # Draw the help panel background
            help_panel = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
            help_panel.fill((80, 80, 120, 230))  # Background color
            
            # Draw border
            pygame.draw.rect(
                help_panel,
                Config.COLORS['BORDER'],
                (0, 0, max_width, total_height),
                3
            )
            
            # Position the panel centered on screen
            panel_x = (Config.SCREEN_WIDTH - max_width) // 2
            panel_y = (Config.SCREEN_HEIGHT - total_height) // 2
            screen.blit(help_panel, (panel_x, panel_y))
            
            # Draw help text
            y_offset = panel_y + padding
            for text in self.help_text:
                text_x = panel_x + (max_width - text.get_width()) // 2
                screen.blit(text, (text_x, y_offset))
                y_offset += text.get_height() + spacing

    def draw_warning_panel(self, screen):
        """Draw the color change warning panel"""
        if self.show_color_warning:
            # Calculate size based on text
            padding = 30
            spacing = 15
            total_height = sum(text.get_height() + spacing for text in self.warning_text) + padding * 2
            max_width = max(text.get_width() for text in self.warning_text) + padding * 2
            
            # Draw the warning panel background (using warning colors)
            warning_panel = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
            warning_panel.fill((200, 100, 50, 240))  # Orange-ish warning color
            
            # Draw border
            pygame.draw.rect(
                warning_panel,
                (255, 150, 50),  # Bright orange border
                (0, 0, max_width, total_height),
                4
            )
            
            # Position the panel centered on screen
            panel_x = (Config.SCREEN_WIDTH - max_width) // 2
            panel_y = (Config.SCREEN_HEIGHT - total_height) // 2
            screen.blit(warning_panel, (panel_x, panel_y))
            
            # Draw warning text
            y_offset = panel_y + padding
            for i, text in enumerate(self.warning_text):
                text_x = panel_x + (max_width - text.get_width()) // 2
                screen.blit(text, (text_x, y_offset))
                y_offset += text.get_height() + spacing
            
            # Draw "Click anywhere to close" at the bottom
            close_font = pygame.font.Font(None, 36)
            close_text = close_font.render(_("Click anywhere to close"), True, (255, 255, 200))
            close_rect = close_text.get_rect(center=(panel_x + max_width // 2, panel_y + total_height - 25))
            screen.blit(close_text, close_rect)

    def run(self):
        # Initialize pygame
        pygame.init()

        # Initialize fonts and help content
        font = pygame.font.Font(None, 64)
        self.help_text = [
            font.render(line, True, (255, 255, 255))  # White text
            for line in [
                _("Four Color Map Puzzle Rules:"),
                _("1. Color each region using one of four colors."),
                _("2. Adjacent regions cannot share the same color."),
                _("3. Use the color buttons to select a color."),
                _("4. Click on a region to apply the selected color."),
                _("5. Complete the map with no adjacent conflicts.")
            ]
        ]
        
        warning_font = pygame.font.Font(None, 52)
        self.warning_text = [
            warning_font.render(line, True, (255, 255, 255))
            for line in [
                _("color Change Not Allowed"),
                _(""),
                _("You cannot change colors while playing!"),
                _(""),
                _("You have already started coloring the map."),
                _("Changing colors now would affect the puzzle."),
                _(""),
                _("Please finish or reset the current game"),
                _("before changing the color set.")
            ]
        ]

        # Initialize the game
        self.game = GameManager()

        if self.activity:
            self.game.set_activity(self.activity)
        
        # Set canvas focus if available
        if self.canvas is not None:
            self.canvas.grab_focus()
        
        # Main game loop
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle GTK events for Sugar integration
            if self.journal:
                # Pump GTK messages
                while Gtk.events_pending():
                    Gtk.main_iteration()
            
            dt = clock.tick(Config.FPS)
            
            # Handle pygame events
            self.check_events()
            
            # Update game state
            if self.game:
                self.game.update(dt)
                
                # Render everything
                self.game.render()
                self.draw_help(pygame.display.get_surface())
                self.draw_warning_panel(pygame.display.get_surface()) 
                
            pygame.display.flip()
        
        # Clean up
        pygame.display.quit()
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    game_instance = main(journal=False)
    game_instance.run()