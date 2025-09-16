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

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, cairo, GLib
import json
import time
import traceback

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from sugar3.graphics.palette import Palette
from gettext import gettext as _

from view.game_engine import GameEngine, GameMode, Region, Config
from view.map_data import LEVELS

class FourColorMap(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        try:
            self.game_engine = GameEngine()
            self._setup_css()
            self._create_toolbar()
            self._create_main_ui()
            self._show_menu()
        except Exception as e:
            print(f"Error in __init__: {e}")
            traceback.print_exc()
    
    def _setup_css(self):
        """Setup CSS styling"""
        try:
            css_provider = Gtk.CssProvider()
            css = b"""
            .menu_button {
                font-size: 14pt;
                min-width: 250px;
                min-height: 60px;
                margin: 8px;
                background-color: #e3f2fd;
                border-radius: 8px;
            }
            
            .menu_button:hover {
                background-color: #bbdefb;
            }
            
            .category_button {
                font-size: 16pt;
                min-width: 200px;
                min-height: 80px;
                margin: 10px;
                border-radius: 10px;
            }
            
            .info_label {
                font-size: 18pt;
                font-weight: bold;
                padding: 20px;
                color: #1565c0;
            }
            """
            
            css_provider.load_from_data(css)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"CSS setup error: {e}")
    
    def _create_toolbar(self):
        try:
            toolbar_box = ToolbarBox()
            self.set_toolbar_box(toolbar_box)
            
            activity_button = ActivityToolbarButton(self)
            toolbar_box.toolbar.insert(activity_button, -1)
            
            separator = Gtk.SeparatorToolItem()
            separator.props.draw = False
            toolbar_box.toolbar.insert(separator, -1)
            
            self.color_button = self._create_color_palette_button()
            toolbar_box.toolbar.insert(self.color_button, -1)
            
            self.eraser_button = ToggleToolButton('edit-clear')
            self.eraser_button.set_tooltip(_('Eraser'))
            self.eraser_button.connect('toggled', self._eraser_toggled_cb)
            toolbar_box.toolbar.insert(self.eraser_button, -1)
            
            separator = Gtk.SeparatorToolItem()
            separator.props.draw = True
            toolbar_box.toolbar.insert(separator, -1)
            
            self.undo_button = ToolButton('edit-undo')
            self.undo_button.set_tooltip(_('Undo'))
            self.undo_button.connect('clicked', self._undo_cb)
            toolbar_box.toolbar.insert(self.undo_button, -1)
            
            self.clear_button = ToolButton('edit-clear')
            self.clear_button.set_tooltip(_('Clear map'))
            self.clear_button.connect('clicked', self._clear_cb)
            toolbar_box.toolbar.insert(self.clear_button, -1)
            
            separator = Gtk.SeparatorToolItem()
            separator.props.draw = True
            toolbar_box.toolbar.insert(separator, -1)
            
            self.zoom_button = self._create_zoom_palette_button()
            toolbar_box.toolbar.insert(self.zoom_button, -1)
            
            separator = Gtk.SeparatorToolItem()
            separator.props.draw = True
            toolbar_box.toolbar.insert(separator, -1)
            
            self.menu_button = ToolButton('go-home')
            self.menu_button.set_tooltip(_('Main Menu'))
            self.menu_button.connect('clicked', self._menu_cb)
            toolbar_box.toolbar.insert(self.menu_button, -1)
            
            self.help_button = ToolButton('toolbar-help')
            self.help_button.set_tooltip(_('Help'))
            self.help_button.connect('clicked', self._help_cb)
            toolbar_box.toolbar.insert(self.help_button, -1)
            
            separator = Gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_expand(True)
            toolbar_box.toolbar.insert(separator, -1)
            
            stop_button = StopButton(self)
            toolbar_box.toolbar.insert(stop_button, -1)
            
            toolbar_box.show_all()
        except Exception as e:
            traceback.print_exc()
    
    def _create_main_ui(self):
        """Create the main game interface"""
        try:
            self.main_vbox = Gtk.VBox(spacing=20)
            self.main_vbox.set_border_width(20)
            title_label = Gtk.Label()
            title_label.set_markup('<span size="xx-large" weight="bold">Four Color Map Puzzle</span>')
            title_label.get_style_context().add_class("info_label")
            self.main_vbox.pack_start(title_label, False, False, 0)

            subtitle_label = Gtk.Label()
            subtitle_label.set_markup('<span size="large">Color the map so no adjacent regions share the same color!</span>')
            subtitle_label.set_line_wrap(True)
            self.main_vbox.pack_start(subtitle_label, False, False, 0)
            
            categories_label = Gtk.Label()
            categories_label.set_markup('<span size="large" weight="bold">Choose a Category:</span>')
            self.main_vbox.pack_start(categories_label, False, False, 10)
            
            categories_container = Gtk.VBox(spacing=10)
            categories_container.set_halign(Gtk.Align.CENTER)
            
            categories = set()
            for level in LEVELS:
                tag = level.get('tag', 'unknown')
                categories.add(tag)
            
            if not categories:
                categories = {'polygons', 'countries'}
            
            for category in sorted(categories):
                category_levels = [l for l in LEVELS if l.get('tag') == category]
                
                button = Gtk.Button()
                button.set_size_request(300, 80)
                button.get_style_context().add_class("category_button")
                
                button_box = Gtk.VBox(spacing=5)
                
                name_label = Gtk.Label()
                name_label.set_markup(f'<span size="large" weight="bold">{category.title()}</span>')
                button_box.pack_start(name_label, False, False, 0)
                
                count_label = Gtk.Label()
                count_label.set_markup(f'<span>{len(category_levels)} levels available</span>')
                button_box.pack_start(count_label, False, False, 0)
                
                button.add(button_box)
                button.connect('clicked', self._show_category_levels, category)
                
                categories_container.pack_start(button, False, False, 0)
            
            self.main_vbox.pack_start(categories_container, True, True, 0)
            
            self.set_canvas(self.main_vbox)
            self.main_vbox.show_all()
            
        except Exception as e:
            traceback.print_exc()
            fallback_box = Gtk.VBox()
            fallback_label = Gtk.Label("Four Color Map - Loading Error")
            fallback_box.pack_start(fallback_label, True, True, 0)
            self.set_canvas(fallback_box)
            fallback_box.show_all()
    
    def _show_menu(self):
        """Show the main menu"""
        try:
            if hasattr(self, 'game_engine'):
                self.game_engine.mode = GameMode.MENU
        except Exception as e:
            print(f"Error showing menu: {e}")
    
    def _show_category_levels(self, button, category_tag):
        """Show levels for selected category"""
        try:
            levels = [level for level in LEVELS if level.get('tag') == category_tag]

            levels_box = Gtk.VBox(spacing=20)
            levels_box.set_border_width(20)
            
            if not levels:
                no_levels = Gtk.Label()
                no_levels.set_markup(f'<span size="large">No {category_tag} maps available yet!</span>')
                levels_box.pack_start(no_levels, True, True, 0)
            else:
                scrolled = Gtk.ScrolledWindow()
                scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
                scrolled.set_min_content_height(400)
                
                levels_container = Gtk.VBox(spacing=10)
                
                for level in levels:
                    level_button = Gtk.Button()
                    level_button.get_style_context().add_class("menu_button")
                    
                    level_box = Gtk.VBox(spacing=5)
                    level_box.set_border_width(10)
                    
                    name_label = Gtk.Label()
                    name_label.set_markup(f'<span size="large" weight="bold">{level["name"]}</span>')
                    name_label.set_halign(Gtk.Align.START)
                    level_box.pack_start(name_label, False, False, 0)
                    
                    desc_label = Gtk.Label()
                    desc_label.set_markup(f'<span>{level["description"]}</span>')
                    desc_label.set_halign(Gtk.Align.START)
                    desc_label.set_line_wrap(True)
                    level_box.pack_start(desc_label, False, False, 0)
                    
                    level_button.add(level_box)
                    level_button.connect('clicked', self._start_level, level)
                    
                    levels_container.pack_start(level_button, False, False, 0)
                
                scrolled.add(levels_container)
                levels_box.pack_start(scrolled, True, True, 0)
            
            self.set_canvas(levels_box)
            levels_box.show_all()
            
        except Exception as e:
            traceback.print_exc()
    
    def _show_menu_ui(self):
        """Return to main menu UI"""
        try:
            self.set_canvas(self.main_vbox)
            self.main_vbox.show_all()
        except Exception as e:
            traceback.print_exc()
    
    def _start_level(self, button, level_data):
        """Start a game level"""
        try:
            self.current_level = level_data
            self.current_level_regions = None
            self.region_colors = {}
            self.selected_color = 0

            self.undo_history = []
            self.max_undo_steps = 20

            self._base_scale = 1.0
            self._current_zoom_level = 1.0
            self._initial_scale_set = False
            self.map_offset_x = 0
            self.map_offset_y = 0
            self.map_scale = 1.0

            self.is_panning = False
            self.pan_start_x = 0
            self.pan_start_y = 0
            self.pan_offset_x = 0
            self.pan_offset_y = 0

            game_vbox = Gtk.VBox()
            
            self.game_area = Gtk.DrawingArea()
            self.game_area.set_size_request(600, 400)
            self.game_area.set_can_focus(True)
            self.game_area.add_events(
                Gdk.EventMask.BUTTON_PRESS_MASK |
                Gdk.EventMask.BUTTON_RELEASE_MASK |
                Gdk.EventMask.SCROLL_MASK |
                Gdk.EventMask.POINTER_MOTION_MASK
            )
            self.game_area.connect('draw', self._draw_game_placeholder, level_data)
            self.game_area.connect('button-press-event', self._on_game_area_click)
            self.game_area.connect('button-release-event', self._on_button_release)
            self.game_area.connect('motion-notify-event', self._on_mouse_motion)
            self.game_area.connect('scroll-event', self._on_scroll)
            game_vbox.pack_start(self.game_area, True, True, 0)
            
            self.set_canvas(game_vbox)
            game_vbox.show_all()
            
        except Exception as e:
            traceback.print_exc()
    
    def _on_button_release(self, widget, event):
        """Handle mouse button release"""
        try:
            if event.button == 2:
                self.is_panning = False
                window = widget.get_window()
                if window:
                    window.set_cursor(None)
                return True
            return False
        except Exception as e:
            return False

    def _on_mouse_motion(self, widget, event):
        """Handle mouse motion for panning"""
        try:
            if self.is_panning:
                dx = event.x - self.pan_start_x
                dy = event.y - self.pan_start_y
                
                self.pan_offset_x = dx
                self.pan_offset_y = dy
                
                widget.queue_draw()
                return True
            return False
        except Exception as e:
            return False

    def _on_scroll(self, widget, event):
        """Handle mouse wheel zoom"""
        return True

    def _on_game_area_click(self, widget, event):
        """Handle clicks on the game area"""
        try:
            if event.button == 2:
                self.is_panning = True
                self.pan_start_x = event.x
                self.pan_start_y = event.y
                window = widget.get_window()
                if window:
                    cursor = Gdk.Cursor.new_for_display(window.get_display(), Gdk.CursorType.FLEUR)
                    window.set_cursor(cursor)
                return True
                
            if event.button != 1:
                return False
                
            if self.is_panning:
                return False
                
            if not hasattr(self, 'current_level_regions') or not self.current_level_regions:
                return False
                
            adjusted_x = event.x - self.pan_offset_x
            adjusted_y = event.y - self.pan_offset_y
            
            base_offset_x = getattr(self, 'map_offset_x', 0)
            base_offset_y = getattr(self, 'map_offset_y', 0)
            current_zoom = getattr(self, '_current_zoom_level', 1.0)
            base_scale = getattr(self, '_base_scale', 1.0)
            
            map_x = (adjusted_x - base_offset_x) / (base_scale * current_zoom)
            map_y = (adjusted_y - base_offset_y) / (base_scale * current_zoom)
            
            for region in self.current_level_regions:
                if self._point_in_region(map_x, map_y, region.get('points', [])):
                    region_id = region.get('id')
                    region_name = region.get('name', f'Region {region_id}')
                    
                    self._save_undo_state()
                    
                    if hasattr(self, 'eraser_button') and self.eraser_button.get_active():
                        if region_id in self.region_colors:
                            del self.region_colors[region_id]
                        else:
                            self._remove_last_undo_state()
                            return True
                    else:
                        old_color = self.region_colors.get(region_id)
                        new_color = self.selected_color
                        
                        if old_color == new_color:
                            self._remove_last_undo_state()
                            return True
                            
                        self.region_colors[region_id] = new_color
                        color_name = ['Red', 'Green', 'Blue', 'Yellow'][new_color]
                    
                    widget.queue_draw()
                    return True
            return True
        except Exception as e:
            return False
    
    def _save_undo_state(self):
        """Save current state for undo"""
        try:
            if not hasattr(self, 'undo_history'):
                self.undo_history = []
                
            current_state = self.region_colors.copy()
            self.undo_history.append(current_state)
            
            if len(self.undo_history) > self.max_undo_steps:
                self.undo_history.pop(0)
                
        except Exception as e:
            print(f"Error saving undo state: {e}")

    def _remove_last_undo_state(self):
        """Remove the last undo state (when action didn't actually change anything)"""
        try:
            if hasattr(self, 'undo_history') and self.undo_history:
                self.undo_history.pop()
        except Exception as e:
            print(f"Error removing undo state: {e}")

    def _undo_cb(self, button):
        """Handle undo - restore previous state"""
        try:
            if not hasattr(self, 'undo_history') or not self.undo_history:
                return
                
            previous_state = self.undo_history.pop()
            self.region_colors = previous_state.copy()
            
            if hasattr(self, 'game_area'):
                self.game_area.queue_draw()
                
        except Exception as e:
            print(f"Error during undo: {e}")

    def _point_in_region(self, x, y, points):
        """Check if point is inside region using ray casting"""
        if len(points) < 3:
            return False
            
        inside = False
        j = len(points) - 1
        
        for i in range(len(points)):
            xi, yi = points[i]
            xj, yj = points[j]
            
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
            
        return inside

    def _draw_game_placeholder(self, widget, cr, level_data):
        """Draw the actual game map from level data"""
        try:
            allocation = widget.get_allocation()
            width = allocation.width
            height = allocation.height
            
            cr.set_source_rgb(0.95, 0.95, 0.95)
            cr.paint()
            
            cr.set_source_rgb(0.7, 0.7, 0.7)
            cr.set_line_width(2)
            cr.rectangle(0, 0, width, height)
            cr.stroke()
            
            regions = []
            if 'data_func' in level_data:
                try:
                    regions = level_data['data_func']()
                except Exception as e:
                    regions = []
            elif 'regions' in level_data:
                regions = level_data['regions']
            
            if not regions:
                cr.set_source_rgb(0.4, 0.4, 0.4)
                cr.select_font_face("Sans", 0, 0)
                cr.set_font_size(24)
                
                text = "No regions defined for this level"
                text_extents = cr.text_extents(text)
                x = (width - text_extents.width) / 2
                y = (height + text_extents.height) / 2
                
                cr.move_to(x, y)
                cr.show_text(text)
                return False
            
            all_points = []
            for region in regions:
                points = region.get('points', [])
                all_points.extend(points)
            
            if not all_points:
                return False
            
            min_x = min(p[0] for p in all_points)
            max_x = max(p[0] for p in all_points)
            min_y = min(p[1] for p in all_points)
            max_y = max(p[1] for p in all_points)
            
            padding = 40
            map_width = max_x - min_x
            map_height = max_y - min_y

            if not hasattr(self, '_base_scale') or not hasattr(self, '_initial_scale_set'):
                if map_width > 0 and map_height > 0:
                    scale_x = (width - 2 * padding) / map_width
                    scale_y = (height - 2 * padding) / map_height
                    self._base_scale = min(scale_x, scale_y)
                    self._initial_scale_set = True
                    self._current_zoom_level = 1.0
                else:
                    self._base_scale = 1.0
                    self._current_zoom_level = 1.0

            current_zoom = getattr(self, '_current_zoom_level', 1.0)
            scale = self._base_scale * current_zoom

            base_offset_x = (width - map_width * scale) / 2 - min_x * scale
            base_offset_y = (height - map_height * scale) / 2 - min_y * scale

            offset_x = base_offset_x + getattr(self, 'pan_offset_x', 0)
            offset_y = base_offset_y + getattr(self, 'pan_offset_y', 0)

            self.map_offset_x = base_offset_x
            self.map_offset_y = base_offset_y
            
            colors = Config.GAME_COLORS
            
            for i, region in enumerate(regions):
                points = region.get('points', [])
                if len(points) < 3:
                    continue
                
                screen_points = []
                for x, y in points:
                    screen_x = x * scale + offset_x
                    screen_y = y * scale + offset_y
                    screen_points.append((screen_x, screen_y))
                
                if hasattr(self, 'region_colors') and region.get('id') in self.region_colors:
                    color_index = self.region_colors[region.get('id')]
                    color = colors[color_index]
                    cr.set_source_rgba(color[0]/255.0, color[1]/255.0, color[2]/255.0, 0.8)
                else:
                    cr.set_source_rgba(0.9, 0.9, 0.9, 1.0)
                
                cr.new_path()
                cr.move_to(screen_points[0][0], screen_points[0][1])
                for point in screen_points[1:]:
                    cr.line_to(point[0], point[1])
                cr.close_path()
                cr.fill_preserve()
                
                cr.set_source_rgb(0.2, 0.2, 0.2)
                cr.set_line_width(2)
                cr.stroke()
                
                region_name = region.get('name', f'Region {region.get("id", i+1)}')
                if region_name and screen_points:
                    center_x = sum(p[0] for p in screen_points) / len(screen_points)
                    center_y = sum(p[1] for p in screen_points) / len(screen_points)
                    
                    cr.set_source_rgb(0, 0, 0)
                    cr.select_font_face("Sans", 0, 0)
                    cr.set_font_size(max(10, min(16, scale * 12)))
                    
                    text_extents = cr.text_extents(region_name)
                    text_x = center_x - text_extents.width/2
                    text_y = center_y + text_extents.height/2
                    
                    bg_padding = 2
                    cr.set_source_rgba(1, 1, 1, 0.8)
                    cr.rectangle(text_x - bg_padding, text_y - text_extents.height - bg_padding,
                            text_extents.width + 2*bg_padding, text_extents.height + 2*bg_padding)
                    cr.fill()
                    
                    cr.set_source_rgb(0, 0, 0)
                    cr.move_to(text_x, text_y)
                    cr.show_text(region_name)
            
            self.map_scale = scale
            self.map_offset_x = offset_x  
            self.map_offset_y = offset_y
            self.current_level_regions = regions
            
        except Exception as e:
            traceback.print_exc()
            
            cr.set_source_rgb(0.4, 0.4, 0.4)
            cr.select_font_face("Sans", 0, 0)
            cr.set_font_size(20)
            text = f"Error rendering map: {str(e)}"
            text_extents = cr.text_extents(text)
            cr.move_to((width - text_extents.width)/2, height/2)
            cr.show_text(text)
        
        if hasattr(self, 'current_level_regions') and self.current_level_regions:
            self._check_completion_and_show_panel(widget)

        return False
    
    def _check_completion_and_show_panel(self, widget):
        """Check if puzzle is complete and show appropriate panel"""
        try:
            if not hasattr(self, 'region_colors') or not self.region_colors:
                return
                
            total_regions = len(self.current_level_regions)
            colored_regions = len(self.region_colors)
            
            if colored_regions < total_regions:
                return
                
            has_conflict = self._check_for_conflicts()
            
            GLib.timeout_add(100, self._show_completion_panel, not has_conflict)
            
        except Exception as e:
            print(f"Error checking completion: {e}")

    def _check_for_conflicts(self):
        """Check if there are any color conflicts between adjacent regions"""
        try:
            adjacencies = {}
            
            for region in self.current_level_regions:
                region_id = region.get('id')
                neighbors = region.get('neighbors', [])
                adjacencies[region_id] = neighbors
            
            for region_id, color in self.region_colors.items():
                neighbors = adjacencies.get(region_id, [])
                for neighbor_id in neighbors:
                    if neighbor_id in self.region_colors:
                        if self.region_colors[neighbor_id] == color:
                            return True
            return False
            
        except Exception as e:
            print(f"Error checking conflicts: {e}")
            return True

    def _show_completion_panel(self, is_success):
        """Show success or failure panel"""
        try:
            from sugar3.graphics import style
            parent_window = self.get_toplevel()
            
            dialog = Gtk.Window()
            dialog.set_modal(True)
            dialog.set_decorated(False)
            dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            dialog.set_border_width(style.LINE_WIDTH)
            dialog.set_transient_for(parent_window)
            
            dialog_width = min(600, max(400, self.get_allocated_width() * 2 // 3))
            dialog_height = min(500, max(350, self.get_allocated_height() * 2 // 3))
            dialog.set_size_request(dialog_width, dialog_height)
            
            main_vbox = Gtk.VBox()
            main_vbox.set_border_width(style.DEFAULT_SPACING)
            dialog.add(main_vbox)
            
            header_box = Gtk.HBox()
            header_box.set_spacing(style.DEFAULT_SPACING)
            
            if is_success:
                title_text = "Puzzle Complete!"
                dialog.set_title("Success!")
            else:
                title_text = "Color Conflict!"
                dialog.set_title("Try Again")
            
            title_label = Gtk.Label()
            title_label.set_markup(f'<span size="x-large" weight="bold">{title_text}</span>')
            header_box.pack_start(title_label, True, True, 0)
            
            close_button = Gtk.Button()
            close_button.set_relief(Gtk.ReliefStyle.NONE)
            close_button.set_size_request(40, 40)
            
            try:
                from sugar3.graphics.icon import Icon
                close_icon = Icon(icon_name='dialog-cancel', pixel_size=24)
                close_button.add(close_icon)
            except:
                close_label = Gtk.Label()
                close_label.set_markup('<span size="x-large" weight="bold">✕</span>')
                close_button.add(close_label)
            
            close_button.connect('clicked', lambda b: dialog.destroy())
            header_box.pack_end(close_button, False, False, 0)
            
            main_vbox.pack_start(header_box, False, False, 0)
            
            separator = Gtk.HSeparator()
            main_vbox.pack_start(separator, False, False, style.DEFAULT_SPACING)
            
            content_vbox = Gtk.VBox()
            content_vbox.set_spacing(style.DEFAULT_SPACING)
            content_vbox.set_margin_left(20)
            content_vbox.set_margin_right(20)
            content_vbox.set_margin_top(20)
            content_vbox.set_margin_bottom(20)
            
            if is_success:
                success_label = Gtk.Label()
                success_label.set_markup("""
    <span size="large">Congratulations!</span>
    <span size="medium">You have successfully colored the entire map using only 4 colors with no adjacent regions sharing the same color!</span>
    """)
                success_label.set_line_wrap(True)
                success_label.set_justify(Gtk.Justification.CENTER)
                success_label.set_halign(Gtk.Align.CENTER)
                content_vbox.pack_start(success_label, True, True, 0)
                
            else:
                failure_label = Gtk.Label()
                failure_label.set_markup("""
    <span size="large">Adjacent regions have the same color!</span>
    <span size="medium">Some neighboring regions are using the same color. In map coloring, adjacent regions must use different colors.</span>
    """)
                failure_label.set_line_wrap(True)
                failure_label.set_justify(Gtk.Justification.LEFT)
                failure_label.set_halign(Gtk.Align.START)
                content_vbox.pack_start(failure_label, True, True, 0)
            
            button_box = Gtk.HBox()
            button_box.set_spacing(10)
            button_box.set_halign(Gtk.Align.CENTER)
            
            if is_success:
                new_level_button = Gtk.Button("Choose New Level")
                new_level_button.connect('clicked', lambda b: (dialog.destroy(), self._menu_cb(None)))
                button_box.pack_start(new_level_button, False, False, 0)
                
                play_again_button = Gtk.Button("Play Again")
                play_again_button.connect('clicked', lambda b: (dialog.destroy(), self._restart_level()))
                button_box.pack_start(play_again_button, False, False, 0)
            else:
                continue_button = Gtk.Button("Continue Coloring")
                continue_button.connect('clicked', lambda b: dialog.destroy())
                button_box.pack_start(continue_button, False, False, 0)
                
                clear_button = Gtk.Button("Clear Map")
                clear_button.connect('clicked', lambda b: (dialog.destroy(), self._clear_cb(None)))
                button_box.pack_start(clear_button, False, False, 0)
            
            content_vbox.pack_start(button_box, False, False, 0)
            main_vbox.pack_start(content_vbox, True, True, 0)
            
            try:
                css_provider = Gtk.CssProvider()
                if is_success:
                    border_color = "#4CAF50"
                    bg_color = "#f1f8e9"
                else:
                    border_color = "#FF9800"
                    bg_color = "#fff3e0"
                
                css_data = f"""
                window {{
                    background-color: {bg_color};
                    border: 3px solid {border_color};
                    border-radius: 12px;
                }}
                label {{
                    color: #333333;
                }}
                button {{
                    border-radius: 8px;
                    min-height: 40px;
                    min-width: 120px;
                    margin: 4px;
                }}
                button:hover {{
                    background-color: rgba(74, 144, 226, 0.1);
                }}
                """.encode('utf-8')
                
                css_provider.load_from_data(css_data)
                style_context = dialog.get_style_context()
                style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            except Exception as css_error:
                print(f"CSS styling failed: {css_error}")
            
            dialog.show_all()
            
            dialog.connect('key-press-event', 
                        lambda d, e: d.destroy() if Gdk.keyval_name(e.keyval) == 'Escape' else False)
            
            return False
            
        except Exception as e:
            print(f"Error showing completion panel: {e}")
            return False

    def _restart_level(self):
        """Restart the current level"""
        try:
            if hasattr(self, 'current_level'):
                self._start_level(None, self.current_level)
        except Exception as e:
            print(f"Error restarting level: {e}")

    def read_file(self, file_path):
        """Load game state from journal"""
        pass
        
    def write_file(self, file_path):
        """Save game state to journal"""
        pass

    def _create_color_palette_button(self):
        """Create a color button with palette"""
        color_button = ToolButton()
        color_button.set_tooltip(_('Select color'))
        
        self._update_color_button_icon(color_button, Config.GAME_COLORS[0])
        
        palette = Palette(_('Colors'))
        hbox = Gtk.HBox(spacing=4)
        
        for i, color in enumerate(Config.GAME_COLORS):
            button = Gtk.Button()
            button.set_size_request(40, 40)
            
            drawing_area = Gtk.DrawingArea()
            drawing_area.set_size_request(32, 32)
            drawing_area.connect('draw', self._draw_color_swatch, color)
            button.add(drawing_area)
            
            button.connect('clicked', self._color_selected_cb, i)
            hbox.pack_start(button, False, False, 0)
        
        palette.set_content(hbox)
        hbox.show_all()
        color_button.set_palette(palette)
        
        return color_button

    def _draw_color_swatch(self, widget, cr, color):
        """Draw color swatch using Cairo"""
        allocation = widget.get_allocation()
        
        cr.set_source_rgb(color[0]/255.0, color[1]/255.0, color[2]/255.0)
        cr.rectangle(0, 0, allocation.width, allocation.height)
        cr.fill()
        
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(2)
        cr.rectangle(1, 1, allocation.width-2, allocation.height-2)
        cr.stroke()

    def _update_color_button_icon(self, button, color):
        """Update color button icon"""
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 32, 32)
        pixbuf.fill((int(color[0]) << 24) | (int(color[1]) << 16) | (int(color[2]) << 8) | 0xff)
        
        icon = Gtk.Image.new_from_pixbuf(pixbuf)
        button.set_icon_widget(icon)
        icon.show()

    def _create_zoom_palette_button(self):
        """Create a zoom button with palette"""
        zoom_button = ToolButton('zoom-original')
        zoom_button.set_tooltip(_('Zoom options'))
        
        palette = Palette(_('Zoom'))
        hbox = Gtk.HBox(spacing=2)
        
        zoom_in = ToolButton('zoom-in')
        zoom_in.set_tooltip(_('Zoom in'))
        zoom_in.connect('clicked', lambda w: (self._zoom_in_cb(w), zoom_button.palette.popdown()))
        hbox.pack_start(zoom_in, False, False, 0)
        
        zoom_out = ToolButton('zoom-out')
        zoom_out.set_tooltip(_('Zoom out'))
        zoom_out.connect('clicked', lambda w: (self._zoom_out_cb(w), zoom_button.palette.popdown()))
        hbox.pack_start(zoom_out, False, False, 0)
        
        zoom_reset = ToolButton('zoom-original')
        zoom_reset.set_tooltip(_('Reset zoom'))
        zoom_reset.connect('clicked', lambda w: (self._zoom_reset_cb(w), zoom_button.palette.popdown()))
        hbox.pack_start(zoom_reset, False, False, 0)
        
        palette.set_content(hbox)
        hbox.show_all()
        zoom_button.set_palette(palette)
        
        return zoom_button

    def _color_selected_cb(self, button, color_index):
        """Handle color selection"""
        self.selected_color = color_index
        color = Config.GAME_COLORS[color_index]
        self._update_color_button_icon(self.color_button, color)
        self.color_button.palette.popdown()
        
        if hasattr(self, 'eraser_button'):
            self.eraser_button.set_active(False)

    def _eraser_toggled_cb(self, button):
        """Handle eraser toggle"""
        if button.get_active():
            print("Eraser activated")
        else:
            print("Eraser deactivated")

    def _clear_cb(self, button):
        """Handle clear - remove all colors from regions with confirmation"""
        try:
            if not hasattr(self, 'region_colors') or not self.region_colors:
                return

            self._save_undo_state()

            cleared_count = len(self.region_colors)
            self.region_colors = {}

            if hasattr(self, 'game_area'):
                self.game_area.queue_draw()

        except Exception as e:
            print(f"Error clearing map: {e}")

    def _zoom_in_cb(self, button):
        """Handle zoom in with multiple levels"""
        if hasattr(self, '_base_scale') and hasattr(self, 'game_area'):
            current_zoom = getattr(self, '_current_zoom_level', 1.0)
            new_zoom = min(current_zoom * 1.25, 8.0)
            
            self._current_zoom_level = new_zoom
            self.game_area.queue_draw()
        else:
            print("Map not loaded for zooming")

    def _zoom_out_cb(self, button):
        """Handle zoom out with multiple levels"""
        if hasattr(self, '_base_scale') and hasattr(self, 'game_area'):
            current_zoom = getattr(self, '_current_zoom_level', 1.0)
            new_zoom = max(current_zoom / 1.25, 0.1)
            
            self._current_zoom_level = new_zoom
            self.game_area.queue_draw()
        else:
            print("Map not loaded for zooming")

    def _zoom_reset_cb(self, button):
        """Handle zoom reset to original size"""
        if hasattr(self, '_base_scale') and hasattr(self, 'game_area'):
            self._current_zoom_level = 1.0
            self.pan_offset_x = 0
            self.pan_offset_y = 0
            self.game_area.queue_draw()
        else:
            print("Map not loaded for zooming")

    def _menu_cb(self, button):
        """Return to main menu"""
        self._show_menu_ui()

    def _help_cb(self, button):
        """Show help dialog"""
        help_message = """Four Color Map Puzzle Help

    Goal: 
    Color all regions on the map using only 4 colors, making sure no adjacent regions share the same color.

    How to Play:
    • Click on a region to color it with the selected color
    • Use the color palette in the toolbar to choose colors
    • Use the eraser to remove colors from regions
    • Pan around large maps by holding middle mouse button and dragging
    • Use zoom controls to get a better view of detailed areas

    Tips:
    • Plan ahead - some regions have many neighbors!
    • The four-color theorem guarantees every map can be colored with just 4 colors
    • Use the undo button if you make a mistake
    • Clear the entire map to start over

    Controls:
    • Left click: Color region
    • Middle click + drag: Pan map
    • Eraser tool: Remove colors
    • Zoom in/out: Better view of map details
    """
        
        self._show_help_dialog("Four Color Map Puzzle Help", help_message)

    def _show_help_dialog(self, title, message):
        """Show custom help dialog with Sugar styling"""
        try:
            from sugar3.graphics import style
            parent_window = self.get_toplevel()
            
            dialog = Gtk.Window()
            dialog.set_title(title)
            dialog.set_modal(True)
            dialog.set_decorated(False)
            dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            dialog.set_border_width(style.LINE_WIDTH)
            dialog.set_transient_for(parent_window)
            
            dialog_width = min(700, max(500, self.get_allocated_width() * 3 // 4))
            dialog_height = min(600, max(400, self.get_allocated_height() * 3 // 4))
            dialog.set_size_request(dialog_width, dialog_height)
            
            main_vbox = Gtk.VBox()
            main_vbox.set_border_width(style.DEFAULT_SPACING)
            dialog.add(main_vbox)
            
            header_box = Gtk.HBox()
            header_box.set_spacing(style.DEFAULT_SPACING)
            
            title_label = Gtk.Label()
            title_label.set_markup(f'<span size="large" weight="bold">🗺️ {title}</span>')
            header_box.pack_start(title_label, True, True, 0)
            
            close_button = Gtk.Button()
            close_button.set_relief(Gtk.ReliefStyle.NONE)
            close_button.set_size_request(40, 40)
            
            try:
                from sugar3.graphics.icon import Icon
                close_icon = Icon(icon_name='dialog-cancel', pixel_size=24)
                close_button.add(close_icon)
            except:
                close_label = Gtk.Label()
                close_label.set_markup('<span size="x-large" weight="bold">✕</span>')
                close_button.add(close_label)
            
            close_button.connect('clicked', lambda b: dialog.destroy())
            header_box.pack_end(close_button, False, False, 0)
            
            main_vbox.pack_start(header_box, False, False, 0)
            
            separator = Gtk.HSeparator()
            main_vbox.pack_start(separator, False, False, style.DEFAULT_SPACING)
            
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_hexpand(True)
            scrolled.set_vexpand(True)
            
            content_label = Gtk.Label()
            content_label.set_text(message)
            content_label.set_halign(Gtk.Align.START)
            content_label.set_valign(Gtk.Align.START)
            content_label.set_line_wrap(True)
            content_label.set_max_width_chars(90)
            content_label.set_selectable(True)
            content_label.set_margin_left(15)
            content_label.set_margin_right(15)
            content_label.set_margin_top(15)
            content_label.set_margin_bottom(15)
            
            scrolled.add(content_label)
            main_vbox.pack_start(scrolled, True, True, 0)
            
            try:
                css_provider = Gtk.CssProvider()
                css_data = """
                window {
                    background-color: #ffffff;
                    border: 3px solid #4A90E2;
                    border-radius: 12px;
                }
                label {
                    color: #333333;
                }
                button {
                    border-radius: 20px;
                }
                button:hover {
                    background-color: rgba(74, 144, 226, 0.1);
                }
                scrolledwindow {
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                }
                """.encode('utf-8')
                
                css_provider.load_from_data(css_data)
                style_context = dialog.get_style_context()
                style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            except Exception as css_error:
                print(f"CSS styling failed: {css_error}")
            
            dialog.show_all()
            
            dialog.connect('key-press-event', 
                        lambda d, e: d.destroy() if Gdk.keyval_name(e.keyval) == 'Escape' else False)
            
        except Exception as e:
            print(f"Error showing help dialog: {e}")
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=title
            )
            dialog.format_secondary_text(message)
            dialog.run()
            dialog.destroy()