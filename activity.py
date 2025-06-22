#
# Copyright (c) 2020 Wade Brainerd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GObject, Gdk
import pygame

from sugar3.activity.activity import Activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton, StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.colorbutton import ColorToolButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from sugar3.graphics.toolcombobox import ToolComboBox
from sugar3.graphics.palettemenu import PaletteMenuBox
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
        self.customize_colors_button.connect('clicked', self._customize_colors_cb)
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
        self.zoom_out_button = ToolButton('zoom-out')
        self.zoom_out_button.set_tooltip(_('Zoom out'))
        self.zoom_out_button.connect('clicked', self._zoom_out_cb)
        toolbar_box.toolbar.insert(self.zoom_out_button, -1)
        self.zoom_out_button.show()

        self.zoom_in_button = ToolButton('zoom-in')
        self.zoom_in_button.set_tooltip(_('Zoom in'))
        self.zoom_in_button.connect('clicked', self._zoom_in_cb)
        toolbar_box.toolbar.insert(self.zoom_in_button, -1)
        self.zoom_in_button.show()

        self.zoom_reset_button = ToolButton('zoom-original')
        self.zoom_reset_button.set_tooltip(_('Reset zoom'))
        self.zoom_reset_button.connect('clicked', self._zoom_reset_cb)
        toolbar_box.toolbar.insert(self.zoom_reset_button, -1)
        self.zoom_reset_button.show()

        # Menu button
        self.menu_button = ToolButton('go-home')  # or pick a more specific icon!
        self.menu_button.set_tooltip(_('Main Menu'))
        self.menu_button.connect('clicked', self._menu_cb)
        toolbar_box.toolbar.insert(self.menu_button, -1)
        self.menu_button.show()

        # Help button
        self.help_button = ToolButton('toolbar-help')
        self.help_button.set_tooltip(_('Help'))
        self.help_button.connect('clicked', self._help_cb)
        
        # Separator before stop button
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()
        
        toolbar_box.toolbar.insert(self.help_button, -1)
        self.help_button.show()

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
        self._update_color_button_icon(color_button, self._rgb_to_hex(Config.GAME_COLORS[0]))
        
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
            self._update_color_button_icon(self.color_palette_button, self._rgb_to_hex(color))
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
        return '#{:02x}{:02x}{:02x}'.format(int(rgb_tuple[0]), int(rgb_tuple[1]), int(rgb_tuple[2]))

    def _update_color_button_icon(self, button, color):
        """Update the color button's icon to show the selected color"""
        # Create a simple colored square icon
        icon_size = 32
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, icon_size, icon_size)
        
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
        cr.rectangle(1, 1, allocation.width - 2, allocation.height - 2)
        cr.stroke()

    def _refresh_color_palette(self):
        """Refresh the color palette with new colors"""
        print(f"DEBUG: Refreshing color palette. Current colors: {Config.GAME_COLORS}")
        
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
            
            print(f"DEBUG: Color palette refreshed with new colors")

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
        
        # If no game in progress or no regions colored, allow color customization
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
            if hasattr(self.game.game, 'selected_color') and self.game.game.selected_color >= 0:
                self.game.game.select_color(self.game.game.selected_color)

    def _undo_cb(self, button):
        """Handle undo"""
        if self.game.game:
            self.game.game.undo_last_action()

    def _clear_cb(self, button):
        """Handle clear/reset"""
        if self.game.game:
            self.game.game.reset_game()

    def _zoom_in_cb(self, button):
        """Handle zoom in"""
        if self.game.game and self.game.game.map_frame:
            self.game.game.map_frame.zoom_level = min(
                self.game.game.map_frame.zoom_level + self.game.game.map_frame.zoom_speed,
                self.game.game.map_frame.max_zoom
            )

    def _zoom_out_cb(self, button):
        """Handle zoom out"""
        if self.game.game and self.game.game.map_frame:
            self.game.game.map_frame.zoom_level = max(
                self.game.game.map_frame.zoom_level - self.game.game.map_frame.zoom_speed,
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
        self.game.read_file(file_path)

    def write_file(self, file_path):
        self.game.write_file(file_path)

    def close(self):
        self.game.quit()

class ColorCustomizationDialog(Gtk.Dialog):
    """Dialog for customizing the game colors"""
    
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, _("Customize Colors"), parent,
                           Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                           (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OK, Gtk.ResponseType.OK))
        
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