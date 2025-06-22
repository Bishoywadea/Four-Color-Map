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
from view.region import Region
from view.config import Config 

class MapFrame:
    def __init__(self, game_manager, center_pos):
        self.game_manager = game_manager
        self.center_pos = center_pos
        self.regions = {}
        
        # Zoom and pan state
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 10.0
        self.zoom_speed = 0.1
        
        # Pan offset (in screen coordinates)
        self.pan_offset = [0, 0]
        self.is_panning = False
        self.pan_start_pos = None
        self.pan_start_offset = None
        
    def setup_regions(self, map_data):
        """Set up regions from map data."""
        self.regions = {}
        
        # Create regions
        for region_data in map_data:
            region = Region(
                region_data['id'],
                region_data['points'],
                region_data.get('name', f"Region {region_data['id']}")
            )
            self.regions[region_data['id']] = region
        
        # Set up neighbors
        for region_data in map_data:
            region = self.regions[region_data['id']]
            for neighbor_id in region_data['neighbors']:
                region.add_neighbor(neighbor_id)
        
        # Center the map on screen initially
        self.center_map()
    
    def center_map(self):
        """Center the map on the screen."""
        if not self.regions:
            return
        
        # Calculate the bounding box of all regions
        all_points = []
        for region in self.regions.values():
            all_points.extend(region.points)
        
        if not all_points:
            return
        
        min_x = min(p[0] for p in all_points)
        max_x = max(p[0] for p in all_points)
        min_y = min(p[1] for p in all_points)
        max_y = max(p[1] for p in all_points)
        
        # Calculate center of the map
        map_center_x = (min_x + max_x) / 2
        map_center_y = (min_y + max_y) / 2
        
        # Calculate offset to center the map
        screen_center_x = self.game_manager.screen.get_width() / 2
        screen_center_y = (self.game_manager.screen.get_height() - Config.UI_HEIGHT) / 2
        
        self.pan_offset[0] = screen_center_x - map_center_x
        self.pan_offset[1] = screen_center_y - map_center_y
    
    def screen_to_world(self, screen_pos):
        """Convert screen coordinates to world coordinates."""
        x, y = screen_pos
        world_x = (x - self.pan_offset[0]) / self.zoom_level
        world_y = (y - self.pan_offset[1]) / self.zoom_level
        return (world_x, world_y)
    
    def world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates."""
        x, y = world_pos
        screen_x = x * self.zoom_level + self.pan_offset[0]
        screen_y = y * self.zoom_level + self.pan_offset[1]
        return (screen_x, screen_y)
    
    def handle_zoom(self, event):
        """Handle mouse wheel zoom."""
        if event.type == pygame.MOUSEWHEEL:
            # Get mouse position for zoom center
            mouse_pos = pygame.mouse.get_pos()
            world_pos_before = self.screen_to_world(mouse_pos)
            
            # Update zoom level
            if event.y > 0:  # Zoom in
                self.zoom_level = min(self.zoom_level + self.zoom_speed, self.max_zoom)
            else:  # Zoom out
                self.zoom_level = max(self.zoom_level - self.zoom_speed, self.min_zoom)
            
            # Adjust pan to keep mouse position fixed
            world_pos_after = self.screen_to_world(mouse_pos)
            dx = (world_pos_before[0] - world_pos_after[0]) * self.zoom_level
            dy = (world_pos_before[1] - world_pos_after[1]) * self.zoom_level
            self.pan_offset[0] += dx
            self.pan_offset[1] += dy
            
            return True
        return False
    
    def handle_pan(self, event):
        """Handle mouse pan with middle button or right button."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2 or event.button == 3:  # Middle or right button
                self.is_panning = True
                self.pan_start_pos = event.pos
                self.pan_start_offset = self.pan_offset.copy()
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2 or event.button == 3:
                self.is_panning = False
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.is_panning:
                dx = event.pos[0] - self.pan_start_pos[0]
                dy = event.pos[1] - self.pan_start_pos[1]
                self.pan_offset[0] = self.pan_start_offset[0] + dx
                self.pan_offset[1] = self.pan_start_offset[1] + dy
                return True
                
        return False
    
    def detect_click(self, mouse_pos):
        """Detect which region was clicked (with zoom transformation)."""
        # Convert mouse position to world coordinates
        world_pos = self.screen_to_world(mouse_pos)
        
        for region in self.regions.values():
            if region.contains_point(world_pos):
                return region.id
        return None
    
    def draw(self):
        """Draw all regions with zoom transformation."""
        for region in self.regions.values():
            # Transform region points to screen coordinates
            screen_points = [self.world_to_screen(p) for p in region.points]
            region.draw_transformed(self.game_manager.screen, screen_points, self.zoom_level)
    
    def reset_view(self):
        """Reset zoom and pan to default."""
        self.zoom_level = 1.0
        self.center_map()

    @property
    def offset_x(self):
        return self.pan_offset[0]

    @property
    def offset_y(self):
        return self.pan_offset[1]

    @offset_x.setter
    def offset_x(self, value):
        self.pan_offset[0] = value

    @offset_y.setter
    def offset_y(self, value):
        self.pan_offset[1] = value