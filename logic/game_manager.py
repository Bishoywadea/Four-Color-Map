import pygame
import time
from view.config import Config
from view.ui import UI
from view.map_frame import MapFrame
from view.menu import Menu

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
        self.puzzle_valid = False 
        self.eraser_mode = False
        self.action_history = []
        self.completion_time = None 

    def start_level(self, level):
        """Start a specific level."""
        self.current_level = level
        self.current_state = self.STATE_PLAYING
        
        # Initialize game components
        self.selected_color = 0
        self.start_time = time.time()
        self.completion_time = None
        self.game_completed = False
        self.puzzle_valid = False
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
        """Color a region with the specified color or erase it."""
        if region_id not in self.map_frame.regions:
            return False
        
        region = self.map_frame.regions[region_id]
        
        # Store the current state for undo
        old_color = region.color
        
        if self.eraser_mode:
            # Erase the color (set to None)
            new_color = None
        else:
            # Apply the selected color
            new_color = Config.GAME_COLORS[color_index]
        
        # Color the region
        region.set_color(new_color)
        
        # Add to action history for undo
        self.action_history.append({
            'region_id': region_id,
            'old_color': old_color,
            'new_color': new_color
        })
        
        # Check if all regions are colored
        if self.are_all_regions_colored():
            self.check_completion()
        else:
            # Reset completion state if puzzle is being modified
            self.game_completed = False
            self.puzzle_valid = False
        
        return True
    
    def are_all_regions_colored(self):
        """Check if all regions have been colored."""
        for region in self.map_frame.regions.values():
            if region.color is None:
                return False
        return True
    
    def check_completion(self):
        """Check if the puzzle is completed and valid."""
        # Mark as completed since all regions are colored
        self.game_completed = True
        
        # Check if the coloring is valid
        self.puzzle_valid = True
        for region in self.map_frame.regions.values():
            for neighbor_id in region.neighbors:
                neighbor = self.map_frame.regions[neighbor_id]
                if region.color == neighbor.color:
                    self.puzzle_valid = False
                    self.completion_time = None 
                    return False
                
        if self.puzzle_valid and self.completion_time is None:
            self.completion_time = time.time()

        return True
    
    def get_elapsed_time(self):
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0
        
        if self.completion_time is not None and self.puzzle_valid:
            return self.completion_time - self.start_time
        else:
            return time.time() - self.start_time
    
    def reset_game(self):
        """Reset the game to initial state."""
        if self.map_frame:
            for region in self.map_frame.regions.values():
                region.set_color(None)
        self.start_time = time.time()
        self.completion_time = None
        self.game_completed = False
        self.puzzle_valid = False
        self.action_history = [] 
        self.eraser_mode = False
        self.selected_color = 0
    
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
    
    def draw_completion_message(self):
        """Draw completion message - shows if puzzle is valid or not."""
        font = pygame.font.Font(None, 48)
        
        if self.puzzle_valid:
            text = font.render("Puzzle Completed Successfully!", True, Config.COLORS['TEXT'])
            color = (0, 255, 0)  # Green for success
        else:
            text = font.render("Invalid Solution - Adjacent regions have same color!", True, Config.COLORS['TEXT'])
            color = (255, 0, 0)  # Red for invalid
        
        text_rect = text.get_rect(center=(Config.SCREEN_WIDTH // 2, 50))
        
        # Draw background for text
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, Config.COLORS['UI_BACKGROUND'], bg_rect)
        pygame.draw.rect(self.screen, color, bg_rect, 3)  # Border color indicates validity
        
        self.screen.blit(text, text_rect)
        
        # Draw time taken
        elapsed = self.get_elapsed_time()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        if self.puzzle_valid:
            time_text = font.render(f"Final Time: {minutes:02d}:{seconds:02d}", True, Config.COLORS['TEXT'])
        else:
            time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, Config.COLORS['TEXT'])
        
        time_rect = time_text.get_rect(center=(Config.SCREEN_WIDTH // 2, 100))
        self.screen.blit(time_text, time_rect)
        
        # Draw appropriate message
        font_small = pygame.font.Font(None, 32)
        if self.puzzle_valid:
            menu_text = font_small.render("Congrats You Solve it Right!", True, Config.COLORS['TEXT'])
        else:
            menu_text = font_small.render("Keep trying! Change colors to fix conflicts", True, Config.COLORS['TEXT'])
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
    
    def undo_last_action(self):
        """Undo the last coloring action."""
        if not self.action_history:
            return
        
        # Pop the last action
        last_action = self.action_history.pop()
        
        # Restore the previous color
        region_id = last_action['region_id']
        old_color = last_action['old_color']
        
        if region_id in self.map_frame.regions:
            self.map_frame.regions[region_id].set_color(old_color)

        self.completion_time = None
        # Check completion state again
        if self.are_all_regions_colored():
            self.check_completion()
        else:
            self.game_completed = False
            self.puzzle_valid = False