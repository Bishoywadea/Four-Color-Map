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

import logging
logger = logging.getLogger(__name__)

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk
import pygame

from sugar3.activity.activity import Activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton, StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from sugar3.graphics.palette import Palette

import sugargame.canvas
import main as main
from gettext import gettext as _
from view.config import Config


class FourColorMap(Activity):
    def __init__(self, handle):
        Activity.__init__(self, handle)

        self.game = main.main()
        self.current_color_set = list(Config.GAME_COLORS)
        self.build_toolbar()

        # Build the Pygame canvas
        self._pygamecanvas = sugargame.canvas.PygameCanvas(
            self, main=self.game.run, modules=[pygame.display]
        )
        self.game.set_canvas(self._pygamecanvas)
        if hasattr(self.game, 'game') and self.game.game:
            self.game.game.set_activity(self)

        self.set_canvas(self._pygamecanvas)
        self._pygamecanvas.grab_focus()

    def build_toolbar(self):
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        # Activity button
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        # Separator
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(False)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        # Color palette button with dynamic update
        self.color_button = self._create_color_palette_button()
        toolbar_box.toolbar.insert(self.color_button, -1)
        self.color_button.show()

        # Color set customization button
        self.customize_colors_button = ToolButton('preferences-system')
        self.customize_colors_button.set_tooltip(_('Customize color set'))
        self.customize_colors_button.connect(
            'clicked', self._customize_colors_cb)
        toolbar_box.toolbar.insert(self.customize_colors_button, -1)
        self.customize_colors_button.show()

        # Eraser button
        self.eraser_button = ToggleToolButton('edit-clear')
        self.eraser_button.set_tooltip(_('Eraser'))
        self.eraser_button.connect('toggled', self._eraser_toggled_cb)
        toolbar_box.toolbar.insert(self.eraser_button, -1)
        self.eraser_button.show()

        # Separator
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = True
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        # Undo button
        self.undo_button = ToolButton('edit-undo')
        self.undo_button.set_tooltip(_('Undo'))
        self.undo_button.connect('clicked', self._undo_cb)
        toolbar_box.toolbar.insert(self.undo_button, -1)
        self.undo_button.show()

        # Clear/Reset button
        self.clear_button = ToolButton('emblem-busy')
        self.clear_button.set_tooltip(_('Clear map'))
        self.clear_button.connect('clicked', self._clear_cb)
        toolbar_box.toolbar.insert(self.clear_button, -1)
        self.clear_button.show()

        # Separator
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = True
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        # Zoom buttons
        self.zoom_button = self._create_zoom_palette_button()
        toolbar_box.toolbar.insert(self.zoom_button, -1)
        self.zoom_button.show()

        # Menu button
        self.menu_button = ToolButton('go-home')
        self.menu_button.set_tooltip(_('Main Menu'))
        self.menu_button.connect('clicked', self._menu_cb)
        toolbar_box.toolbar.insert(self.menu_button, -1)
        self.menu_button.show()

        # Help button
        self.help_button = ToolButton('toolbar-help')
        self.help_button.set_tooltip(_('Help'))
        self.help_button.connect('clicked', self._help_cb)
        toolbar_box.toolbar.insert(self.help_button, -1)
        self.menu_button.show()

        # Separator before stop button
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        # Stop button
        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.show_all()

    def _create_color_palette_button(self):
        """Create a color button with palette that updates dynamically"""
        # Create the main color button
        color_button = ToolButton()
        color_button.set_tooltip(_('Select color'))

        # Create initial icon with current first color
        self._update_color_button_icon(
            color_button, self._rgb_to_hex(
                Config.GAME_COLORS[0]))

        # Store reference for updates
        self.color_palette_button = color_button

        # Create palette
        palette = self._create_color_palette()
        color_button.set_palette(palette)

        return color_button

    def _create_color_palette(self):
        """Create the color palette with current colors"""
        palette = Palette(_('Colors'))

        # Create a box to hold color swatches
        hbox = Gtk.HBox()

        # Create buttons for each current color in Config.GAME_COLORS
        self.color_buttons = []  # Store references to update later

        for i, color in enumerate(Config.GAME_COLORS):
            # Create a button for each color
            button = Gtk.Button()
            button.set_size_request(40, 40)

            # Create a drawing area for the color
            drawing_area = Gtk.DrawingArea()
            drawing_area.set_size_request(32, 32)
            button.add(drawing_area)

            # Store the index and current color
            button.color_index = i
            drawing_area.color = color  # Store as RGB tuple

            # Connect draw signal
            drawing_area.connect('draw', self._color_swatch_draw_cb_rgb, color)

            # Connect click handler
            button.connect('clicked', self._color_selected_cb_index, i)

            hbox.pack_start(button, False, False, 2)
            self.color_buttons.append(button)

        palette.set_content(hbox)
        hbox.show_all()

        return palette

    def _color_selected_cb_index(self, button, color_index):
        """Handle color selection by index"""
        if self.game and self.game.game:
            self.game.game.select_color(color_index)
            # Update button icon with current color
            color = Config.GAME_COLORS[color_index]
            self._update_color_button_icon(
                self.color_palette_button, self._rgb_to_hex(color))
            self.color_palette_button.palette.popdown()

            # Make sure eraser is not selected
            self.eraser_button.set_active(False)

    def _color_swatch_draw_cb_rgb(self, widget, cr, rgb_color):
        """Draw a color swatch using RGB tuple"""
        allocation = widget.get_allocation()

        # Use RGB values directly
        r = rgb_color[0] / 255.0
        g = rgb_color[1] / 255.0
        b = rgb_color[2] / 255.0

        cr.set_source_rgb(r, g, b)
        cr.rectangle(0, 0, allocation.width, allocation.height)
        cr.fill()

        # Draw border
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(2)
        cr.rectangle(1, 1, allocation.width - 2, allocation.height - 2)
        cr.stroke()

    def _rgb_to_hex(self, rgb_tuple):
        """Convert RGB tuple to hex string"""
        return '#{:02x}{:02x}{:02x}'.format(
            int(rgb_tuple[0]), int(rgb_tuple[1]), int(rgb_tuple[2]))

    def _update_color_button_icon(self, button, color):
        """Update the color button's icon to show the selected color"""
        # Create a simple colored square icon
        icon_size = 32
        pixbuf = GdkPixbuf.Pixbuf.new(
            GdkPixbuf.Colorspace.RGB, True, 8, icon_size, icon_size)

        # Parse color
        if isinstance(color, str):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
        else:
            r, g, b = color

        # Fill with color
        pixbuf.fill((r << 24) | (g << 16) | (b << 8) | 0xff)

        # Create icon
        icon = Gtk.Image.new_from_pixbuf(pixbuf)
        button.set_icon_widget(icon)
        icon.show()

    def _color_swatch_draw_cb(self, widget, cr, color):
        """Draw a color swatch"""
        allocation = widget.get_allocation()

        # Parse color
        r = int(color[1:3], 16) / 255.0
        g = int(color[3:5], 16) / 255.0
        b = int(color[5:7], 16) / 255.0

        cr.set_source_rgb(r, g, b)
        cr.rectangle(0, 0, allocation.width, allocation.height)
        cr.fill()

        # Draw border
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(2)
    def _refresh_color_palette(self):
        """Refresh the color palette with new colors"""
        logger.debug(
            f"DEBUG: Refreshing color palette. Current colors: {
                Config.GAME_COLORS}")

        # Get the toolbar and remove the old color button completely
        toolbar = self.get_toolbar_box().toolbar
        if hasattr(self, 'color_palette_button') and self.color_palette_button:
            # Find the position of the color button
            position = toolbar.get_item_index(self.color_palette_button)
            toolbar.remove(self.color_palette_button)

            # Create a new color button
            self.color_button = self._create_color_palette_button()
            toolbar.insert(self.color_button, position)
            self.color_button.show()
            logger.debug(
                f"DEBUG: New color palette created with colors: {
                    Config.GAME_COLORS}")

    def _color_selected_cb(self, button, color_index, color, color_button):
        """Handle color selection"""
        self.game.game.select_color(color_index)
        self._update_color_button_icon(color_button, color)
        color_button.palette.popdown()

        self.eraser_button.set_active(False)

    def _customize_colors_cb(self, button):
        """Open color customization dialog"""
        # Check if a game is in progress
        if (hasattr(self.game, 'game') and self.game.game and
                self.game.game.current_state == self.game.game.STATE_PLAYING):

            # Check if any region has been colored
            has_colored_regions = False
            if self.game.game.map_frame:
                for region in self.game.game.map_frame.regions.values():
                    if region.color is not None:
                        has_colored_regions = True
                        break

            if has_colored_regions:
                # Show warning dialog
                if hasattr(self.game, 'show_color_warning'):
                    self.game.show_color_warning = True
                return

        # If no game in progress or no regions colored, allow color
        # customization
        dialog = ColorCustomizationDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            # Colors were changed, refresh the palette
            self._refresh_color_palette()

            # Notify the game to update any cached colors
            if self.game and self.game.game:
                # Force a redraw with new colors
                self.game.game.refresh_colors()

        dialog.destroy()

    def _eraser_toggled_cb(self, button):
        """Handle eraser toggle"""
        if button.get_active():
            self.game.game.select_eraser()
        else:
            # Reselect the current color
            if (hasattr(self.game.game, 'selected_color')
                    and self.game.game.selected_color >= 0):
                self.game.game.select_color(self.game.game.selected_color)

    def _undo_cb(self, button):
        """Handle undo"""
        if self.game.game:
            self.game.game.undo_last_action()

    def _clear_cb(self, button):
        """Handle clear/reset"""
        if self.game.game:
            self.game.game.reset_game()

    def _create_zoom_palette_button(self):
        """Create a zoom button with a palette for zoom options."""
        # Create the main button that will be visible on the toolbar
        zoom_button = ToolButton('zoom-original')
        zoom_button.set_tooltip(_('Zoom options'))
        self.zoom_palette_button = zoom_button  # Store a reference

        # Create the palette that will pop up
        palette = self._create_zoom_palette()
        zoom_button.set_palette(palette)

        return zoom_button

    def _create_zoom_palette(self):
        """Create the palette containing the individual zoom buttons."""
        palette = Palette(_('Zoom'))

        # Use an HBox to arrange the buttons horizontally
        hbox = Gtk.HBox()

        # --- Zoom In Button ---
        zoom_in = ToolButton('zoom-in')
        zoom_in.set_tooltip(_('Zoom in'))
        # We use a lambda to call the original function and then close the
        # palette
        zoom_in.connect(
            'clicked',
            lambda w: (
                self._zoom_in_cb(w),
                self.zoom_palette_button.palette.popdown()))
        hbox.pack_start(zoom_in, False, False, 2)

        # --- Zoom Out Button ---
        zoom_out = ToolButton('zoom-out')
        zoom_out.set_tooltip(_('Zoom out'))
        zoom_out.connect(
            'clicked',
            lambda w: (
                self._zoom_out_cb(w),
                self.zoom_palette_button.palette.popdown()))
        hbox.pack_start(zoom_out, False, False, 2)

        # --- Reset Zoom Button ---
        zoom_reset = ToolButton('zoom-original')
        zoom_reset.set_tooltip(_('Reset zoom'))
        zoom_reset.connect(
            'clicked',
            lambda w: (
                self._zoom_reset_cb(w),
                self.zoom_palette_button.palette.popdown()))
        hbox.pack_start(zoom_reset, False, False, 2)

        palette.set_content(hbox)
        hbox.show_all()

        return palette

    def _zoom_in_cb(self, button):
        """Handle zoom in"""
        if self.game.game and self.game.game.map_frame:
            self.game.game.map_frame.zoom_level = min(
                (self.game.game.map_frame.zoom_level
                 + self.game.game.map_frame.zoom_speed),
                self.game.game.map_frame.max_zoom
            )

    def _zoom_out_cb(self, button):
        """Handle zoom out"""
        if self.game.game and self.game.game.map_frame:
            self.game.game.map_frame.zoom_level = max(
                self.game.game.map_frame.zoom_level
                - self.game.game.map_frame.zoom_speed,
                self.game.game.map_frame.min_zoom
            )

    def _zoom_reset_cb(self, button):
        """Handle zoom reset"""
        if self.game.game and self.game.game.map_frame:
            self.game.game.map_frame.reset_view()

    def _menu_cb(self, button):
        """Return to the level category menu."""
        if hasattr(self.game, 'game') and self.game.game:
            if hasattr(self.game.game, 'return_to_menu'):
                self.game.game.return_to_menu()
        if hasattr(self.game, 'show_help'):
            self.game.show_help = False
        if hasattr(self.game, 'show_color_warning'):
            self.game.show_color_warning = False

    def _help_cb(self, button):
        """Handle help button"""
        self.game.toggle_help()

    def read_file(self, file_path):
        """Read game state from journal"""
        import json
        import os

        logger.debug(f"read_file() called with path: {file_path}")
        logger.debug(f"File path: {file_path}")

        if not os.path.exists(file_path):
            logger.debug(
                f"[DEBUG] File does not exist: {file_path}")
            return

        if not self.game:
            logger.debug(
                "[DEBUG] ERROR: self.game is None, cannot read file")
            return

        try:
            with open(file_path, 'r') as f:
                save_data = json.load(f)

            logger.debug(
                f"[DEBUG] Loaded save data with keys: {list(save_data.keys())}")
            logger.debug(
                f"[DEBUG] Current game state: {save_data.get('game_state', 'Not found')}"
            )
            logger.debug(
                f"[DEBUG] Regions to restore: {len(save_data.get('regions', {}))}"
            )

            # Restore color configuration if present
            if 'color_config' in save_data:
                from view.config import Config
                Config.GAME_COLORS = [
                    tuple(color) for color in save_data['color_config']]
                logger.debug(
                    f"[DEBUG] Restored color configuration: {Config.GAME_COLORS}")

            # Check if we have a playing state to restore
            if (save_data.get('game_state') == 'playing'
                    and 'playing_state' in save_data):
                playing_state = save_data['playing_state']
                level_info = playing_state['level']

                logger.debug(
                    f"[DEBUG] Restoring game - Level: {level_info['name']}")
                logger.debug(
                    f"[DEBUG] Regions to restore: "
                    f"{len(playing_state.get('regions', {}))}"
                )

                # Import LEVELS here to avoid circular import
                from view.map_data import LEVELS

                # Find the level by index or name
                level_to_load = None
                level_index = level_info.get('level_index', -1)

                if 0 <= level_index < len(LEVELS):
                    level_to_load = LEVELS[level_index]
                else:
                    # Fallback: find by name
                    for level in LEVELS:
                        if level['name'] == level_info['name']:
                            level_to_load = level
                            break

                if level_to_load:
                    # Start the level
                    logger.debug(
                        f"[DEBUG] Level to load: {level_to_load['name']}, "
                        f"index: {level_index}")
                    self.game.start_level(level_to_load)

                    # Restore the game state after level is loaded
                    if self.game.map_frame:
                        # Restore region colors
                        for region_id_str, region_data in playing_state.get(
                                'regions', {}).items():
                            region_id = int(region_id_str)
                            if region_id in self.game.map_frame.regions:
                                color = tuple(region_data['color'])
                                self.game.map_frame.regions[region_id].color = color
                                logger.debug(
                                    f"[DEBUG] Restored color for region {region_id}: "
                                    f"{color}")

                        # Restore view state
                        if 'view' in playing_state:
                            view = playing_state['view']
                            self.game.map_frame.zoom_level = view.get(
                                'zoom_level', 1.0)
                            self.game.map_frame.pan_offset[0] = view.get(
                                'offset_x', 0)
                            self.game.map_frame.pan_offset[1] = view.get(
                                'offset_y', 0)
                            logger.debug(
                                f"[DEBUG] Restored view - zoom: {self.game.map_frame.zoom_level}, "
                                f"offset: {self.game.map_frame.pan_offset}")

                    # Restore game properties
                    self.game.selected_color = playing_state.get(
                        'selected_color', 0)
                    self.game.eraser_mode = playing_state.get(
                        'eraser_mode', False)
                    self.game.game_completed = playing_state.get(
                        'game_completed', False)
                    self.game.puzzle_valid = playing_state.get(
                        'puzzle_valid', False)
                    self.game.action_history = playing_state.get(
                        'action_history', [])

                    # Restore timing
                    if 'start_time_offset' in playing_state:
                        import time
                        self.game.start_time = time.time(
                        ) - playing_state['start_time_offset']
                        logger.debug(
                            f"[DEBUG] Restored start time: {self.game.start_time}"
                        )

                    if playing_state.get('completion_time') is not None:
                        self.game.completion_time = self.game.start_time + \
                            playing_state['completion_time']

                    # Update UI elements if needed
                    if hasattr(self.game, 'update_ui'):
                        self.game.update_ui()

                    logger.debug(
                        "[DEBUG] Game state restored successfully")
                    logger.debug("[DEBUG] Read operation: SUCCESS")
                else:
                    logger.debug(
                        f"[DEBUG] ERROR: Could not find level '{level_info['name']}'")
                    logger.debug(
                        "[DEBUG] Read operation: FAILED - Level not found")
            else:
                logger.debug(
                    "[DEBUG] Game state is not 'playing' or no playing state found")
                logger.debug(
                    "[DEBUG] Read operation: SUCCESS - No playing state found")

        except json.JSONDecodeError as e:
            logger.debug(
                f"[DEBUG] JSONDecodeError: {type(e).__name__}: {e}")
            logger.debug("[DEBUG] Read operation: FAILED - JSON decode error")
        except Exception as e:
            logger.debug(
                f"[DEBUG] ERROR: Unexpected error reading journal - "
                f"{type(e).__name__}: {e}")
            import traceback
            logger.debug(
                f"[DEBUG] Traceback: {traceback.format_exc()}")
            logger.debug("[DEBUG] Read operation: FAILED")

    def write_file(self, file_path):
        """Write game state to journal"""
        import json
        import os
        logger.debug(f"write_file() called with path: {file_path}")
        logger.debug(f"File path: {file_path}")
        logger.debug(
            f"Directory exists: {os.path.exists(os.path.dirname(file_path))}")

        if not self.game:
            logger.debug(
                "[DEBUG] ERROR: self.game is None, cannot write file")
            return

        save_data = None

        try:
            # Get save data directly - no need for workarounds since
            # get_save_data is fixed
            save_data = self.game.get_save_data()

            if not save_data:
                logger.debug(
                    "[DEBUG] ERROR: get_save_data() returned None or empty")
                return

            logger.debug(
                f"[DEBUG] Got save data with keys: {list(save_data.keys())}")

            if 'playing_state' in save_data:
                ps = save_data['playing_state']
                logger.debug(
                    f"[DEBUG] Playing state - Level index: "
                    f"{ps.get('level', {}).get('level_index', -1)}"
                )
                logger.debug(
                    f"[DEBUG] Playing state - Selected color: "
                    f"{ps.get('selected_color', 'Not set')}"
                )

            # Convert to JSON
            json_data = json.dumps(save_data, indent=2)

            # Write to file
            with open(file_path, 'w') as f:
                bytes_written = f.write(json_data)
                logger.debug(
                    f"[DEBUG] Successfully wrote save data to {file_path}")

            # Verify the write
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                
                logger.debug(
                    f"[DEBUG] File successfully written, size: {file_size} bytes"
                )
            else:
                logger.debug(
                    "[DEBUG] ERROR: File does not exist after write!")

        except IOError as e:
            logger.debug(
                f"[DEBUG] IOError: {type(e).__name__}: {e}")
            logger.debug("[DEBUG] Write operation: FAILED - IOError")
        except Exception as e:
            logger.debug(
                f"[DEBUG] ERROR: Unexpected error writing journal - "
                f"{type(e).__name__}: {e}")
            if save_data is not None:
                logger.debug(
                    f"[DEBUG] save_data keys: {list(save_data.keys())}")
            else:
                logger.debug(
                    f"[DEBUG] Traceback: {e.__traceback__}")

    def close(self):
        import os
        self.write_file(
            os.path.join(
                os.path.expanduser("~"),
                "Desktop",
                "dummy.txt"))
        self.game.quit()


class ColorCustomizationDialog(Gtk.Dialog):
    """Dialog for customizing the game colors"""

    def __init__(self, parent):
        Gtk.Dialog.__init__(
            self,
            _("Customize Colors"),
            parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK
            )
        )

        self.set_default_size(400, 300)

        # Create main container
        vbox = Gtk.VBox(spacing=10)
        vbox.set_border_width(10)

        # Instructions
        label = Gtk.Label(_("Click on a color to change it:"))
        vbox.pack_start(label, False, False, 0)

        # Color grid
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_halign(Gtk.Align.CENTER)

        self.color_buttons = []

        for i in range(4):
            # Color label
            label = Gtk.Label(_("Color {}").format(i + 1))
            grid.attach(label, 0, i, 1, 1)

            # Color button
            color_button = Gtk.ColorButton()

            # Set current color
            rgba = Gdk.RGBA()
            rgba.red = Config.GAME_COLORS[i][0] / 255.0
            rgba.green = Config.GAME_COLORS[i][1] / 255.0
            rgba.blue = Config.GAME_COLORS[i][2] / 255.0
            rgba.alpha = 1.0
            color_button.set_rgba(rgba)

            color_button.connect('color-set', self._color_changed_cb, i)
            grid.attach(color_button, 1, i, 1, 1)
            self.color_buttons.append(color_button)

        vbox.pack_start(grid, True, True, 0)

        # Reset button
        reset_button = Gtk.Button(_("Reset to Default Colors"))
        reset_button.connect('clicked', self._reset_colors_cb)
        vbox.pack_start(reset_button, False, False, 0)

        # Add to dialog
        content_area = self.get_content_area()
        content_area.add(vbox)

        self.show_all()

    def _color_changed_cb(self, button, color_index):
        """Handle color change"""
        rgba = button.get_rgba()
        Config.GAME_COLORS[color_index] = (
            int(rgba.red * 255),
            int(rgba.green * 255),
            int(rgba.blue * 255)
        )

    def _reset_colors_cb(self, button):
        """Reset colors to default"""
        Config.reset_colors()

        # Update all color buttons
        for i, color_button in enumerate(self.color_buttons):
            rgba = Gdk.RGBA()
            rgba.red = Config.GAME_COLORS[i][0] / 255.0
            rgba.green = Config.GAME_COLORS[i][1] / 255.0
            rgba.blue = Config.GAME_COLORS[i][2] / 255.0
            rgba.alpha = 1.0
            color_button.set_rgba(rgba)
