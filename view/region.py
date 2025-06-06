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
        """Calculate the bounding rectangle for efficient collision detection."""
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
        """Check if a point is inside this region using ray casting algorithm."""
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
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def draw(self, surface):
        """Draw the region on the given surface."""
        # Fill the region
        pygame.draw.polygon(surface, self.get_color(), self.points)
        
        # Draw border
        pygame.draw.polygon(surface, Config.COLORS['BORDER'], self.points, Config.BORDER_WIDTH)

    def apply_offset(self, offset):
        """Apply an offset to all vertices of the region."""
        self.vertices = [(x + offset[0], y + offset[1]) for x, y in self.vertices]
        # Recalculate the bounding rect after applying offset
        x_coords = [v[0] for v in self.vertices]
        y_coords = [v[1] for v in self.vertices]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    