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
import time
from view.config import Config
from view.ui import UI
from view.map_frame import MapFrame
from view.menu import Menu


class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        
        pygame.display.set_caption("Four Color Map Puzzle")

        self.STATE_MENU = "menu"
        self.STATE_PLAYING = "playing"
        self.current_state = self.STATE_MENU

        self.menu = Menu(self)

        self.selected_color = 0
        self.start_time = None
        self.game_completed = False
        self.ui = None
        self.map_frame = None
        self.current_level = None
        self.puzzle_valid = False
        self.eraser_mode = False
        self.action_history = []
        self.completion_time = None
        self.activity = None

    def get_screen_dimensions(self):
        """Get current screen dimensions dynamically."""
        return self.screen.get_width(), self.screen.get_height()

    def set_activity(self, activity):
        """Set reference to the activity for communication."""
        self.activity = activity

    def start_level(self, level):
        """Start a specific level."""
        self.current_level = level
        self.current_state = self.STATE_PLAYING

        self.selected_color = 0
        self.start_time = time.time()
        self.completion_time = None
        self.game_completed = False
        self.puzzle_valid = False
        self.ui = UI(self)

        screen_width, screen_height = self.get_screen_dimensions()
        available_height = screen_height - Config.UI_HEIGHT
        center_x = screen_width // 2
        center_y = available_height // 2
        self.map_frame = MapFrame(self, (center_x, center_y))

        level_data = level["data_func"]()
        self.load_map(level_data)

    def load_map(self, map_data):
        """Load a map from the provided data."""
        self.map_frame.setup_regions(map_data)

    def handle_event(self, event):
        """Handle game events."""
        if self.current_state == self.STATE_MENU:
            if self.menu.handle_event(event):
                self.start_level(self.menu.selected_level)
                self.refresh_colors()

        elif self.current_state == self.STATE_PLAYING:
            if self.ui.handle_event(event):
                return

            if self.map_frame and self.map_frame.handle_zoom(event):
                return

            if self.map_frame and self.map_frame.handle_pan(event):
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.map_frame.is_panning:
                    region_id = self.map_frame.detect_click(event.pos)
                    if region_id is not None:
                        self.color_region(region_id, self.selected_color)

    def color_region(self, region_id, color_index):
        """Color a region with the specified color or erase it."""
        if region_id not in self.map_frame.regions:
            return False

        region = self.map_frame.regions[region_id]

        old_color = region.color

        if self.eraser_mode:
            new_color = None
        else:
            new_color = Config.GAME_COLORS[color_index]

        region.set_color(new_color)

        self.action_history.append(
            {"region_id": region_id,
             "old_color": old_color,
             "new_color": new_color}
        )

        if self.are_all_regions_colored():
            self.check_completion()
        else:
            self.game_completed = False
            self.puzzle_valid = False

        if self.activity and hasattr(self.activity, "update_toolbar_state"):
            self.activity.update_toolbar_state()

        return True

    def are_all_regions_colored(self):
        """Check if all regions have been colored."""
        for region in self.map_frame.regions.values():
            if region.color is None:
                return False
        return True

    def check_completion(self):
        """Check if the puzzle is completed and valid."""
        self.game_completed = True

        self.puzzle_valid = True
        for region in self.map_frame.regions.values():
            for neighbor_id in region.neighbors:
                neighbor = self.map_frame.regions[neighbor_id]
                if region.color == neighbor.color:
                    self.puzzle_valid = False
                    self.completion_time = None
                    return False

        if self.puzzle_valid and self.completion_time is None:
            self.completion_time = time.time()

        return True

    def get_elapsed_time(self):
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0

        if self.completion_time is not None and self.puzzle_valid:
            return self.completion_time - self.start_time
        else:
            return time.time() - self.start_time

    def reset_game(self):
        """Reset the game to initial state."""
        if self.map_frame:
            for region in self.map_frame.regions.values():
                region.set_color(None)
        self.start_time = time.time()
        self.completion_time = None
        self.game_completed = False
        self.puzzle_valid = False
        self.action_history = []
        self.eraser_mode = False
        self.selected_color = 0
        if self.activity and hasattr(self.activity, "update_toolbar_state"):
            self.activity.update_toolbar_state()

    def update(self, dt):
        """Update game state."""
        if self.current_state == self.STATE_PLAYING and self.ui:
            self.ui.update(dt)

    def render(self):
        """Render the game."""
        if self.current_state == self.STATE_MENU:
            self.menu.draw(self.screen)

        elif self.current_state == self.STATE_PLAYING:
            self.screen.fill((240, 248, 255))

            if self.map_frame:
                self.map_frame.draw()

            if self.ui:
                self.ui.draw(self.screen)

            if self.game_completed:
                self.draw_completion_message()

            self.draw_level_name()

    def draw_completion_message(self):
        """Draw completion message."""
        screen_width, screen_height = self.get_screen_dimensions()
        
        font_large = pygame.font.Font(None, 64)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)

        if self.puzzle_valid:
            main_text = "Puzzle Completed Successfully!"
            text_surface = font_large.render(main_text, True, (255, 255, 255))
            bg_color = (50, 200, 50)
        else:
            main_text = "Oops! Adjacent regions have the same color!"
            text_surface = font_large.render(main_text, True, (255, 255, 255))
            bg_color = (200, 50, 50) 

        text_rect = text_surface.get_rect(center=(screen_width // 2, 80))

        bg_rect = text_rect.inflate(60, 30)
        pygame.draw.rect(self.screen, bg_color, bg_rect)
        self.screen.blit(text_surface, text_rect)

        elapsed = self.get_elapsed_time()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        if self.puzzle_valid:
            time_text = f"Final Time: {minutes:02d}:{seconds:02d}"
            time_color = (255, 255, 100)
        else:
            time_text = f"Current Time: {minutes:02d}:{seconds:02d}"
            time_color = (255, 255, 255)

        time_surface = font_medium.render(time_text, True, time_color)
        time_rect = time_surface.get_rect(center=(screen_width // 2, 140))

        time_bg_rect = time_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (50, 50, 50), time_bg_rect)
        self.screen.blit(time_surface, time_rect)

        if self.puzzle_valid:
            congrats_text = "Amazing! You solved it perfectly!"
            msg_color = (255, 255, 100)
        else:
            congrats_text = "Keep trying! Change colors to fix conflicts"
            msg_color = (255, 200, 200)

        msg_surface = font_small.render(congrats_text, True, msg_color)
        msg_rect = msg_surface.get_rect(center=(screen_width // 2, 190))

        msg_bg_rect = msg_rect.inflate(30, 15)
        pygame.draw.rect(self.screen, (30, 30, 30), msg_bg_rect)
        self.screen.blit(msg_surface, msg_rect)

    def draw_level_name(self):
        """Draw the current level name."""
        if self.current_level:
            font = pygame.font.Font(None, 42)
            level_text = f"{self.current_level['name']}"
            text_surface = font.render(level_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(topleft=(30, 30))

            bg_rect = text_rect.inflate(30, 20)
            pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
            self.screen.blit(text_surface, text_rect)

    def undo_last_action(self):
        """Undo the last coloring action."""
        if not self.action_history:
            return

        last_action = self.action_history.pop()

        region_id = last_action["region_id"]
        old_color = last_action["old_color"]

        if region_id in self.map_frame.regions:
            self.map_frame.regions[region_id].set_color(old_color)

        self.completion_time = None

        if self.are_all_regions_colored():
            self.check_completion()
        else:
            self.game_completed = False
            self.puzzle_valid = False

    def select_color(self, color_index):
        """Select a color for painting regions."""
        self.selected_color = color_index
        self.eraser_mode = False

    def select_eraser(self):
        """Select eraser mode."""
        self.eraser_mode = True
        self.selected_color = -1

    def refresh_colors(self):
        """Refresh the display with new colors"""
        if self.current_state == "playing" and self.map_frame:
            pass

        if self.activity:
            self.activity._refresh_color_palette()

    def return_to_menu(self):
        self.current_state = self.STATE_MENU
        self.menu.selected_level = None
