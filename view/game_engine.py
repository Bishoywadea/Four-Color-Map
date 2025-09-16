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

import time
import math
from enum import Enum
from gi.repository import cairo

class GameMode(Enum):
    MENU = 1
    PLAYING = 2
    COMPLETED = 3

class Config:
    GAME_COLORS = [
        (255, 100, 100),
        (100, 255, 100),
        (100, 100, 255),
        (255, 255, 100),
    ]
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    UNCOLORED = (240, 240, 240)
    BORDER_COLOR = (50, 50, 50)
    SELECTED_COLOR = (255, 255, 255)
    BORDER_WIDTH = 2

class Region:
    def __init__(self, region_id, points, name="", neighbors=None):
        self.id = region_id
        self.points = points
        self.name = name
        self.color_index = None
        self.neighbors = set(neighbors or [])
        
    def set_color(self, color_index):
        """Set the region's color by index"""
        self.color_index = color_index
        
    def get_color(self):
        """Get the region's current color as RGB tuple"""
        if self.color_index is not None:
            return Config.GAME_COLORS[self.color_index]
        return Config.UNCOLORED
        
    def contains_point(self, x, y):
        """Point-in-polygon test using ray casting algorithm"""
        if len(self.points) < 3:
            return False
            
        inside = False
        j = len(self.points) - 1
        
        for i in range(len(self.points)):
            xi, yi = self.points[i]
            xj, yj = self.points[j]
            
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
            
        return inside

class GameEngine:
    def __init__(self):
        self.config = Config()
        self.mode = GameMode.MENU
        self.regions = {}
        self.selected_color = 0
        self.eraser_mode = False
        self.current_level = None
        self.start_time = None
        
        self.zoom_level = 1.0
        self.min_zoom = 0.3
        self.max_zoom = 5.0
        self.zoom_speed = 0.1
        self.pan_offset = [0, 0]
        self.is_panning = False
        self.pan_start = None
        
        self.history = []
        
    def set_mode(self, mode):
        """Set the current game mode"""
        self.mode = mode
        
    def start_level(self, level_data):
        """Start a new level"""
        self.current_level = level_data
        self.mode = GameMode.PLAYING
        self.start_time = time.time()
        self.history = []
        
        regions_data = []
        if 'data_func' in level_data:
            try:
                regions_data = level_data['data_func']()
            except Exception as e:
                regions_data = []
        elif 'regions' in level_data:
            regions_data = level_data['regions']
        
        self.regions = {}
        for region_data in regions_data:
            region = Region(
                region_data['id'],
                region_data['points'],
                region_data.get('name', f"Region {region_data['id']}"),
                region_data.get('neighbors', [])
            )
            self.regions[region_data['id']] = region
            
        self._fit_map_to_screen()
        
    def _fit_map_to_screen(self):
        """Fit the map to screen with padding"""
        if not self.regions:
            return
        all_points = []
        for region in self.regions.values():
            all_points.extend(region.points)
            
        if not all_points:
            return
            
        min_x = min(p[0] for p in all_points)
        max_x = max(p[0] for p in all_points)
        min_y = min(p[1] for p in all_points)
        max_y = max(p[1] for p in all_points)
        
        map_width = max_x - min_x
        map_height = max_y - min_y
        
        if map_width > 0 and map_height > 0:
            screen_width = 800
            screen_height = 600
            
            zoom_x = (screen_width * 0.8) / map_width
            zoom_y = (screen_height * 0.8) / map_height
            
            self.zoom_level = min(zoom_x, zoom_y)
            self.zoom_level = max(self.min_zoom, min(self.max_zoom, self.zoom_level))
            
            map_center_x = (min_x + max_x) / 2
            map_center_y = (min_y + max_y) / 2
            
            self.pan_offset = [
                screen_width / 2 - map_center_x * self.zoom_level,
                screen_height / 2 - map_center_y * self.zoom_level
            ]
    
    def get_elapsed_time(self):
        """Get elapsed time since level start"""
        if self.start_time and self.mode == GameMode.PLAYING:
            return time.time() - self.start_time
        return 0
        
    def select_color(self, color_index):
        """Select a color for painting"""
        self.selected_color = color_index
        self.eraser_mode = False
        
    def select_eraser(self):
        """Select eraser mode"""
        self.eraser_mode = True
        
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x * self.zoom_level + self.pan_offset[0]
        screen_y = world_y * self.zoom_level + self.pan_offset[1]
        return (screen_x, screen_y)
        
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x - self.pan_offset[0]) / self.zoom_level
        world_y = (screen_y - self.pan_offset[1]) / self.zoom_level
        return (world_x, world_y)
        
    def handle_click(self, x, y, button):
        """Handle mouse click"""
        if button == 1:
            world_x, world_y = self.screen_to_world(x, y)
            
            for region in self.regions.values():
                if region.contains_point(world_x, world_y):
                    self.history.append({
                        'region_id': region.id,
                        'old_color': region.color_index
                    })
                    
                    if self.eraser_mode:
                        region.set_color(None)
                    else:
                        region.set_color(self.selected_color)
                    break
                    
        elif button == 2 or button == 3:
            self.is_panning = True
            self.pan_start = (x, y)
            
    def handle_button_release(self, x, y, button):
        """Handle mouse button release"""
        if button == 2 or button == 3:
            self.is_panning = False
            
    def handle_mouse_motion(self, x, y):
        """Handle mouse motion"""
        if self.is_panning and self.pan_start:
            dx = x - self.pan_start[0]
            dy = y - self.pan_start[1]
            self.pan_offset[0] += dx
            self.pan_offset[1] += dy
            self.pan_start = (x, y)
            
    def zoom_in(self, center_x=None, center_y=None):
        """Zoom in, optionally around a point"""
        if center_x is not None and center_y is not None:
            self._zoom_at_point(center_x, center_y, 1 + self.zoom_speed)
        else:
            self.zoom_level = min(self.zoom_level * (1 + self.zoom_speed), self.max_zoom)
            
    def zoom_out(self, center_x=None, center_y=None):
        """Zoom out, optionally around a point"""
        if center_x is not None and center_y is not None:
            self._zoom_at_point(center_x, center_y, 1 - self.zoom_speed)
        else:
            self.zoom_level = max(self.zoom_level * (1 - self.zoom_speed), self.min_zoom)
            
    def _zoom_at_point(self, center_x, center_y, zoom_factor):
        """Zoom in/out around a specific point"""
        old_world_pos = self.screen_to_world(center_x, center_y)
        
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, self.zoom_level * zoom_factor))
        
        new_world_pos = self.screen_to_world(center_x, center_y)
        
        dx = (old_world_pos[0] - new_world_pos[0]) * self.zoom_level
        dy = (old_world_pos[1] - new_world_pos[1]) * self.zoom_level
        self.pan_offset[0] += dx
        self.pan_offset[1] += dy
        
    def reset_zoom(self):
        """Reset zoom and pan to fit map"""
        self._fit_map_to_screen()
        
    def undo(self):
        """Undo the last action"""
        if self.history:
            last_action = self.history.pop()
            region = self.regions.get(last_action['region_id'])
            if region:
                region.set_color(last_action['old_color'])
                
    def clear_map(self):
        """Clear all colors from the map"""
        for region in self.regions.values():
            region.set_color(None)
        self.history = []
        
    def is_puzzle_complete(self):
        """Check if the puzzle is complete (all regions colored and valid)"""
        if not self.regions:
            return False
            
        for region in self.regions.values():
            if region.color_index is None:
                return False
                
        for region in self.regions.values():
            region_color = region.color_index
            for neighbor_id in region.neighbors:
                neighbor = self.regions.get(neighbor_id)
                if neighbor and neighbor.color_index == region_color:
                    return False
                    
        return True
        
    def draw(self, cr, width, height):
        """Draw the game using Cairo"""
        if hasattr(self, '_screen_width') and (self._screen_width != width or self._screen_height != height):
            self._fit_map_to_screen()
        self._screen_width = width
        self._screen_height = height
        
        cr.set_source_rgb(0.95, 0.95, 0.95)
        cr.paint()
        
        for region in self.regions.values():
            self._draw_region(cr, region)
            
        if self.is_puzzle_complete():
            self._draw_completion_overlay(cr, width, height)
            
    def _draw_region(self, cr, region):
        """Draw a single region"""
        if len(region.points) < 3:
            return
            
        screen_points = [self.world_to_screen(x, y) for x, y in region.points]
        
        cr.new_path()
        cr.move_to(screen_points[0][0], screen_points[0][1])
        for point in screen_points[1:]:
            cr.line_to(point[0], point[1])
        cr.close_path()
        
        color = region.get_color()
        cr.set_source_rgb(color[0]/255.0, color[1]/255.0, color[2]/255.0)
        cr.fill_preserve()
        
        border_width = max(1, self.config.BORDER_WIDTH * self.zoom_level)
        cr.set_line_width(border_width)
        cr.set_source_rgb(
            self.config.BORDER_COLOR[0]/255.0, 
            self.config.BORDER_COLOR[1]/255.0, 
            self.config.BORDER_COLOR[2]/255.0
        )
        cr.stroke()
        
        if self.zoom_level > 1.0 and region.name:
            self._draw_region_label(cr, region, screen_points)
            
    def _draw_region_label(self, cr, region, screen_points):
        """Draw region name label"""
        center_x = sum(p[0] for p in screen_points) / len(screen_points)
        center_y = sum(p[1] for p in screen_points) / len(screen_points)
        
        font_size = max(10, min(20, 12 * self.zoom_level))
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(font_size)
        
        text_extents = cr.text_extents(region.name)
        text_width = text_extents.width
        text_height = text_extents.height
        
        padding = 2
        bg_x = center_x - text_width/2 - padding
        bg_y = center_y - text_height/2 - padding
        bg_width = text_width + 2*padding
        bg_height = text_height + 2*padding
        
        cr.set_source_rgba(1, 1, 1, 0.8)
        cr.rectangle(bg_x, bg_y, bg_width, bg_height)
        cr.fill()
        
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(center_x - text_width/2, center_y + text_height/2)
        cr.show_text(region.name)
        
    def _draw_completion_overlay(self, cr, width, height):
        """Draw completion celebration overlay"""
        cr.set_source_rgba(0, 0, 0, 0.3)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        cr.set_source_rgb(1, 1, 1)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(48)
        
        text = "🎉 Puzzle Complete! 🎉"
        text_extents = cr.text_extents(text)
        x = (width - text_extents.width) / 2
        y = height / 2
        
        cr.move_to(x, y)
        cr.show_text(text)
        
    def save_state(self):
        """Save game state for journal"""
        if not self.current_level:
            return {}
            
        regions_state = {}
        for region_id, region in self.regions.items():
            regions_state[region_id] = region.color_index
            
        return {
            'mode': self.mode.value,
            'current_level': self.current_level,
            'regions_state': regions_state,
            'selected_color': self.selected_color,
            'eraser_mode': self.eraser_mode,
            'start_time': self.start_time,
            'zoom_level': self.zoom_level,
            'pan_offset': self.pan_offset,
            'history': self.history
        }
        
    def load_state(self, data):
        """Load game state from journal"""
        try:
            if 'current_level' in data and data['current_level']:
                self.start_level(data['current_level'])
                
                if 'regions_state' in data:
                    for region_id, color_index in data['regions_state'].items():
                        if region_id in self.regions:
                            self.regions[region_id].set_color(color_index)
                            
                self.selected_color = data.get('selected_color', 0)
                self.eraser_mode = data.get('eraser_mode', False)
                self.start_time = data.get('start_time')
                self.zoom_level = data.get('zoom_level', 1.0)
                self.pan_offset = data.get('pan_offset', [0, 0])
                self.history = data.get('history', [])
                
                if 'mode' in data:
                    self.mode = GameMode(data['mode'])
                    
        except Exception as e:
            print(f"Error loading state: {e}")
