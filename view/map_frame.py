from view.region import Region

class MapFrame:
    def __init__(self, game_manager, center_pos):
        self.game_manager = game_manager
        self.center_pos = center_pos
        self.regions = {}
        
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
    
    def detect_click(self, mouse_pos):
        """Detect which region was clicked."""
        for region in self.regions.values():
            if region.rect.collidepoint(mouse_pos) and region.contains_point(mouse_pos):
                return region.id
        return None
    
    def draw(self):
        """Draw all regions."""
        for region in self.regions.values():
            region.draw(self.game_manager.screen)