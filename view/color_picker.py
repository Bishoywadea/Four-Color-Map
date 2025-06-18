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
from view.config import Config

class SimpleColorPicker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color_options = [
            # Row 1 - Reds/Pinks
            (255, 0, 0),     # Red
            (220, 20, 60),   # Crimson
            (255, 99, 71),   # Tomato
            (255, 192, 203), # Pink
            (255, 105, 180), # Hot Pink
            
            # Row 2 - Blues
            (0, 0, 255),     # Blue
            (0, 191, 255),   # Deep Sky Blue
            (100, 149, 237), # Cornflower Blue
            (70, 130, 180),  # Steel Blue
            (0, 0, 139),     # Dark Blue
            
            # Row 3 - Greens
            (0, 255, 0),     # Green
            (50, 205, 50),   # Lime Green
            (34, 139, 34),   # Forest Green
            (144, 238, 144), # Light Green
            (0, 128, 0),     # Dark Green
            
            # Row 4 - Yellows/Oranges
            (255, 255, 0),   # Yellow
            (255, 215, 0),   # Gold
            (255, 165, 0),   # Orange
            (255, 140, 0),   # Dark Orange
            (255, 69, 0),    # Orange Red
            
            # Row 5 - Purples
            (128, 0, 128),   # Purple
            (148, 0, 211),   # Dark Violet
            (186, 85, 211),  # Medium Orchid
            (218, 112, 214), # Orchid
            (221, 160, 221), # Plum
            
            # Row 6 - Browns/Others
            (139, 69, 19),   # Saddle Brown
            (160, 82, 45),   # Sienna
            (210, 105, 30),  # Chocolate
            (128, 128, 128), # Gray
            (64, 64, 64),    # Dark Gray
        ]
        
        self.cell_size = 40
        self.cols = 5
        self.rows = 6
        self.spacing = 5
        
        self.selected_color = None
        
    def handle_event(self, event):
        """Handle color picker events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                
                # Check if click is within picker bounds
                rel_x = mouse_x - self.x
                rel_y = mouse_y - self.y
                
                if 0 <= rel_x <= self.cols * (self.cell_size + self.spacing):
                    if 0 <= rel_y <= self.rows * (self.cell_size + self.spacing):
                        # Calculate which color was clicked
                        col = rel_x // (self.cell_size + self.spacing)
                        row = rel_y // (self.cell_size + self.spacing)
                        
                        index = row * self.cols + col
                        index = int(index)
                        if 0 <= index < len(self.color_options):
                            self.selected_color = self.color_options[index]
                            return True
        return False
    
    def draw(self, surface):
        """Draw the color picker grid."""
        for i, color in enumerate(self.color_options):
            row = i // self.cols
            col = i % self.cols
            
            x = self.x + col * (self.cell_size + self.spacing)
            y = self.y + row * (self.cell_size + self.spacing)
            
            rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            
            # Draw color square
            pygame.draw.rect(surface, color, rect)
            
            # Draw border (thicker if selected)
            if color == self.selected_color:
                pygame.draw.rect(surface, (255, 255, 255), rect, 3)
            else:
                pygame.draw.rect(surface, Config.COLORS['BORDER'], rect, 1)