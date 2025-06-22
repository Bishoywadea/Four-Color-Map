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

    def get_save_data(self):
        """Get the current game state as a dictionary for saving"""
        print("[DEBUG] get_save_data() called")

        if not self.game:
            print("[DEBUG] ERROR: self.game is None in get_save_data")
            return {}

        print(f"[DEBUG] Current game state: {self.game.current_state}")

        save_data = {
            'version': 1,
            'game_state': self.game.current_state,
        }

        # Save current game session data
        if (self.game.current_state == self.game.STATE_PLAYING
           and self.game.current_level):
            # Import here to avoid circular import
            from view.map_data import LEVELS

            print("[DEBUG] Saving playing state")
            print(f"[DEBUG] Current level: {self.game.current_level['name']}")
            print(f"[DEBUG] Game completed: {self.game.game_completed}")
            print(f"[DEBUG] Puzzle valid: {self.game.puzzle_valid}")

            save_data['playing_state'] = {
                'level': {
                    'name': self.game.current_level['name'],
                    'tag': self.game.current_level.get('tag', ''),
                    'description': self.game.current_level.get('description', ''),
                    'level_index': LEVELS.index(self.game.current_level) if self.game.current_level in LEVELS else -1
                },
                'start_time_offset': self.game.get_elapsed_time(),
                'completion_time': self.game.completion_time - self.game.start_time if self.game.completion_time else None,
                'game_completed': self.game.game_completed,
                'puzzle_valid': self.game.puzzle_valid,
                'selected_color': self.game.selected_color,
                'eraser_mode': self.game.eraser_mode,
                'action_history': self.game.action_history,
                'regions': {}
            }

            # Save region colors
            colored_regions = 0
            if self.game.map_frame:
                for region_id, region in self.game.map_frame.regions.items():
                    if region.color is not None:
                        save_data['playing_state']['regions'][region_id] = {
                            'color': list(region.color)
                        }
                        colored_regions += 1

                print(
                    f"[DEBUG] Saving {colored_regions} colored regions out of {
                        len(
                            self.game.map_frame.regions)} total")

                # Save zoom and pan state
                save_data['playing_state']['view'] = {
                    'zoom_level': self.game.map_frame.zoom_level,
                    'offset_x': self.game.map_frame.pan_offset[0],
                    'offset_y': self.game.map_frame.pan_offset[1]
                }
                print(
                    f"[DEBUG] Saving view state - zoom: {self.game.map_frame.zoom_level}")
        else:
            print("[DEBUG] Not in playing state or no current level")

        # Save color configuration
        save_data['color_config'] = [list(color)
                                     for color in Config.GAME_COLORS]
        print(f"[DEBUG] Saving {len(Config.GAME_COLORS)} custom colors")

        print("[DEBUG] Save data prepared successfully")
        return save_data

    def load_from_journal(self, save_data):
        """Load game state from journal data"""
        import time
        from view.map_data import LEVELS

        print("[DEBUG] load_from_journal() called")
        print(
            f"[DEBUG] Save data keys: {
                list(
                    save_data.keys()) if save_data else 'None'}")

        if not save_data:
            print("[DEBUG] ERROR: No save data provided")
            return

        if not self.game:
            print("[DEBUG] ERROR: self.game is None")
            return

        # Restore color configuration
        if 'color_config' in save_data:
            Config.GAME_COLORS = [tuple(color)
                                  for color in save_data['color_config']]
            print("[DEBUG] Restored {len(Config.GAME_COLORS)} custom colors")

            # Refresh the activity's color palette if available
            if self.activity:
                self.activity._refresh_color_palette()
                print("[DEBUG] Refreshed activity color palette")

        # Check if we were playing a level
        saved_state = save_data.get('game_state')
        print(f"[DEBUG] Saved game state: {saved_state}")

        if saved_state == self.game.STATE_PLAYING and 'playing_state' in save_data:
            playing_state = save_data['playing_state']
            level_name = playing_state['level'].get('name', 'Unknown')
            print(f"[DEBUG] Loading playing state for level: {level_name}")

            # Find and load the level
            level_index = playing_state['level'].get('level_index', -1)
            print(f"[DEBUG] Level index: {level_index}")

            if level_index >= 0 and level_index < len(LEVELS):
                level = LEVELS[level_index]
                print(f"[DEBUG] Found level: {level['name']}")

                # Start the level
                self.game.start_level(level)
                print("[DEBUG] Started level")

                # Restore timing
                if playing_state.get('start_time_offset'):
                    self.game.start_time = time.time(
                    ) - playing_state['start_time_offset']
                    print(
                        f"[DEBUG] Restored elapsed time: {
                            playing_state['start_time_offset']} seconds")

                if playing_state.get('completion_time') is not None:
                    self.game.completion_time = self.game.start_time + \
                        playing_state['completion_time']
                    print("[DEBUG] Restored completion time")

                # Restore game state
                self.game.game_completed = playing_state.get(
                    'game_completed', False)
                self.game.puzzle_valid = playing_state.get(
                    'puzzle_valid', False)
                self.game.selected_color = playing_state.get(
                    'selected_color', 0)
                self.game.eraser_mode = playing_state.get('eraser_mode', False)
                self.game.action_history = playing_state.get(
                    'action_history', [])

                print(
                    f"[DEBUG] Restored game flags - completed: {
                        self.game.game_completed}, valid: {
                        self.game.puzzle_valid}")

                # Restore region colors
                if self.game.map_frame and 'regions' in playing_state:
                    restored_regions = 0
                    for region_id, region_data in playing_state['regions'].items(
                    ):
                        if region_id in self.game.map_frame.regions:
                            color = tuple(
                                region_data['color']) if region_data.get('color') else None
                            self.game.map_frame.regions[region_id].set_color(
                                color)
                            restored_regions += 1
                    print(
                        f"[DEBUG] Restored colors for {restored_regions} regions")

                # Restore view state
                if self.game.map_frame and 'view' in playing_state:
                    view = playing_state['view']
                    self.game.map_frame.zoom_level = view.get(
                        'zoom_level', 1.0)
                    self.game.map_frame.offset_x = view.get('offset_x', 0)
                    self.game.map_frame.offset_y = view.get('offset_y', 0)
                    print(
                        f"[DEBUG] Restored view state - zoom: {self.game.map_frame.zoom_level}")

                # Regenerate completion effects if puzzle was completed
                if self.game.game_completed and self.game.puzzle_valid:
                    self.game.generate_completion_stars()
                    print("[DEBUG] Regenerated completion stars")

                # Update toolbar state
                if self.activity and hasattr(self.activity, 'eraser_button'):
                    self.activity.eraser_button.set_active(
                        self.game.eraser_mode)
                    print("[DEBUG] Updated toolbar eraser state")

                print("[DEBUG] Successfully restored game state")
            else:
                print(f"[DEBUG] ERROR: Invalid level index {level_index}")
        else:
            # If not in playing state, just stay at the menu
            self.game.current_state = self.game.STATE_MENU
            print("[DEBUG] No playing state to restore, staying at menu")

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
            total_height = sum(
                text.get_height() + spacing for text in self.help_text) + padding * 2
            max_width = max(text.get_width()
                            for text in self.help_text) + padding * 2

            # Draw the help panel background
            help_panel = pygame.Surface(
                (max_width, total_height), pygame.SRCALPHA)
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
            total_height = sum(
                text.get_height() + spacing for text in self.warning_text) + padding * 2
            max_width = max(text.get_width()
                            for text in self.warning_text) + padding * 2

            # Draw the warning panel background (using warning colors)
            warning_panel = pygame.Surface(
                (max_width, total_height), pygame.SRCALPHA)
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
            close_text = close_font.render(
                _("Click anywhere to close"), True, (255, 255, 200))
            close_rect = close_text.get_rect(
                center=(
                    panel_x + max_width // 2,
                    panel_y + total_height - 25))
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
