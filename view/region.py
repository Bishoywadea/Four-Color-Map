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


class Region:
    def __init__(self, region_id, points, name=""):
        self.id = region_id
        self.points = points  # List of (x, y) coordinates defining the polygon
        self.name = name
        self.color = None  # None means uncolored
        self.neighbors = set()  # Set of neighboring region IDs
        self.rect = self._calculate_bounding_rect()

    def _calculate_bounding_rect(self):
        """
            Calculate the bounding rectangle for efficient collision detection.
        """
        if not self.points:
            return pygame.Rect(0, 0, 0, 0)

        min_x = min(point[0] for point in self.points)
        max_x = max(point[0] for point in self.points)
        min_y = min(point[1] for point in self.points)
        max_y = max(point[1] for point in self.points)

        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def add_neighbor(self, region_id):
        """Add a neighboring region."""
        self.neighbors.add(region_id)

    def set_color(self, color):
        """Set the region's color."""
        self.color = color

    def get_color(self):
        """Get the region's current color."""
        return self.color if self.color else Config.COLORS['UNCOLORED']

    def contains_point(self, point):
        """
            Check if a point is inside this region using ray casting algorithm.
        """
        x, y = point
        n = len(self.points)
        inside = False

        p1x, p1y = self.points[0]
        for i in range(1, n + 1):
            p2x, p2y = self.points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / \
                                (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def draw(self, surface):
        """Draw the region on the given surface."""
        # Fill the region
        pygame.draw.polygon(surface, self.get_color(), self.points)

        # Draw border
        pygame.draw.polygon(
            surface,
            Config.COLORS['BORDER'],
            self.points,
            Config.BORDER_WIDTH)

    def draw_transformed(self, surface, screen_points, zoom_level):
        """Draw the region with transformed points."""
        if len(screen_points) < 3:
            return

        # Fill the region
        pygame.draw.polygon(surface, self.get_color(), screen_points)

        # Adjust border width based on zoom level
        border_width = max(1, int(Config.BORDER_WIDTH * zoom_level))

        # Draw border
        pygame.draw.polygon(
            surface,
            Config.COLORS['BORDER'],
            screen_points,
            border_width)
