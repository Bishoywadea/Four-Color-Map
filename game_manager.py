import pygame
import time
from config import Config
from map_data import get_sample_map
from ui import UI
from map_frame import MapFrame
from menu import Menu

class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        screen_info = pygame.display.Info()
        Config.SCREEN_WIDTH = screen_info.current_w
        Config.SCREEN_HEIGHT = screen_info.current_h
        
        pygame.display.set_caption("Four Color Map Puzzle")
        
        # Game states
        self.STATE_MENU = "menu"
        self.STATE_PLAYING = "playing"
        self.current_state = self.STATE_MENU
        
        # Menu
        self.menu = Menu(self)

        # Game components (initialized when level is selected)
        self.selected_color = 0
        self.start_time = None
        self.game_completed = False
        self.ui = None
        self.map_frame = None
        self.current_level = None

    def start_level(self, level):
        """Start a specific level."""
        self.current_level = level
        self.current_state = self.STATE_PLAYING
        
        # Initialize game components
        self.selected_color = 0
        self.start_time = time.time()
        self.game_completed = False
        self.ui = UI(self)
        
        # Create map frame centered on screen
        # Account for UI height at the bottom
        available_height = Config.SCREEN_HEIGHT - Config.UI_HEIGHT
        center_x = Config.SCREEN_WIDTH // 2
        center_y = available_height // 2
        self.map_frame = MapFrame(self, (center_x, center_y))
        
        # Load the level data
        level_data = level['data_func']()
        self.load_map(level_data)

    def load_map(self, map_data):
        """Load a map from the provided data."""
        self.map_frame.setup_regions(map_data)
        
    
    def handle_event(self, event):
        """Handle game events."""
        if self.current_state == self.STATE_MENU:
            if self.menu.handle_event(event):
                # Level was selected
                self.start_level(self.menu.selected_level)

        elif self.current_state == self.STATE_PLAYING:
            # Check for ESC key to return to menu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
                    return
            
            if self.ui.handle_event(event):
                return  # UI handled the event
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    region_id = self.map_frame.detect_click(event.pos)
                    if region_id is not None:
                        self.color_region(region_id, self.selected_color)
                
    
    def return_to_menu(self):
        """Return to the main menu."""
        self.current_state = self.STATE_MENU
        self.menu.selected_level = None
        
    def color_region(self, region_id, color_index):
        """Color a region with the specified color."""
        if region_id not in self.map_frame.regions:
            return False
        
        region = self.map_frame.regions[region_id]
        new_color = Config.GAME_COLORS[color_index]
        
        # Check if this coloring is valid
        if self.is_valid_coloring(region_id, color_index):
            region.set_color(new_color)
            self.check_completion()
            return True
        
        return False
    
    def is_valid_coloring(self, region_id, color_index):
        """Check if coloring a region with the given color is valid."""
        region = self.map_frame.regions[region_id]
        new_color = Config.GAME_COLORS[color_index]
        
        # Check all neighbors
        for neighbor_id in region.neighbors:
            neighbor = self.map_frame.regions[neighbor_id]
            if neighbor.color == new_color:
                return False
        
        return True
    
    def check_completion(self):
        """Check if the puzzle is completed."""
        # All regions must be colored
        for region in self.map_frame.regions.values():
            if region.color is None:
                return False
        
        # All colorings must be valid
        for region in self.map_frame.regions.values():
            for neighbor_id in region.neighbors:
                neighbor = self.map_frame.regions[neighbor_id]
                if region.color == neighbor.color:
                    return False
        
        self.game_completed = True
        return True
    
    def get_elapsed_time(self):
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time
    
    def reset_game(self):
        """Reset the game to initial state."""
        if self.map_frame:
            for region in self.map_frame.regions.values():
                region.set_color(None)
        self.start_time = time.time()
        self.game_completed = False
    
    def update(self, dt):
        """Update game state."""
        if self.current_state == self.STATE_PLAYING and self.ui:
            self.ui.update(dt)
    
    def render(self):
        """Render the game."""
        if self.current_state == self.STATE_MENU:
            self.menu.draw(self.screen)
            
        elif self.current_state == self.STATE_PLAYING:
            # Clear screen
            self.screen.fill(Config.COLORS['BACKGROUND'])
            
            # Draw map frame
            if self.map_frame:
                self.map_frame.draw()
            
            # Draw UI
            if self.ui:
                self.ui.draw(self.screen)
            
            # Draw completion message
            if self.game_completed:
                self.draw_completion_message()
            
            # Draw level name in top-left
            self.draw_level_name()
            
            # Draw return to menu hint
            self.draw_menu_hint()
    
    def draw_completion_message(self):
        """Draw completion message."""
        font = pygame.font.Font(None, 48)
        text = font.render("Puzzle Completed!", True, Config.COLORS['TEXT'])
        text_rect = text.get_rect(center=(Config.SCREEN_WIDTH // 2, 50))
        
        # Draw background for text
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, Config.COLORS['UI_BACKGROUND'], bg_rect)
        pygame.draw.rect(self.screen, Config.COLORS['BORDER'], bg_rect, 2)
        
        self.screen.blit(text, text_rect)
        
        # Draw time taken
        elapsed = self.get_elapsed_time()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, Config.COLORS['TEXT'])
        time_rect = time_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 100))
        self.screen.blit(time_text, time_rect)
        
        # Draw return to menu message
        font_small = pygame.font.Font(None, 32)
        menu_text = font_small.render("Press ESC to return to menu", True, Config.COLORS['TEXT'])
        menu_rect = menu_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 150))
        self.screen.blit(menu_text, menu_rect)
    
    def draw_level_name(self):
        """Draw the current level name."""
        if self.current_level:
            font = pygame.font.Font(None, 36)
            text = font.render(self.current_level['name'], True, Config.COLORS['TEXT'])
            text_rect = text.get_rect(topleft=(20, 20))
            
            # Draw background
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, Config.COLORS['UI_BACKGROUND'], bg_rect)
            pygame.draw.rect(self.screen, Config.COLORS['BORDER'], bg_rect, 2)
            
            self.screen.blit(text, text_rect)
    
    def draw_menu_hint(self):
        """Draw hint to return to menu."""
        font = pygame.font.Font(None, 24)
        text = font.render("ESC - Menu", True, Config.COLORS['TEXT'])
        text_rect = text.get_rect(topright=(Config.SCREEN_WIDTH - 20, 20))
        self.screen.blit(text, text_rect)