import pygame
import time
import math
import random
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
        
        # Animation and visual enhancement variables
        self.completion_stars = []

    def generate_completion_stars(self):
        """Generate celebration stars when puzzle is completed."""
        self.completion_stars = []
        for _ in range(20):
            x = random.randint(100, Config.SCREEN_WIDTH - 100)
            y = random.randint(100, Config.SCREEN_HEIGHT - 200)
            size = random.randint(4, 12)
            speed = random.uniform(1.0, 3.0)
            angle = random.uniform(0, math.pi * 2)
            self.completion_stars.append({
                'x': x, 'y': y, 'size': size, 
                'speed': speed, 'angle': angle,
                'life': 1.0, 'original_size': size
            })

    def draw_star(self, screen, x, y, size, color=(255, 255, 100)):
        """Draw a cute star shape (same as menu)."""
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                # Outer points
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
            else:
                # Inner points
                px = x + (size * 0.4) * math.cos(angle)
                py = y + (size * 0.4) * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(screen, color, points)

    def draw_gradient_background(self, screen):
        """Draw a gentle gradient background for gameplay."""
        # Softer gradient for gameplay (less distracting than menu)
        for y in range(Config.SCREEN_HEIGHT):
            ratio = y / Config.SCREEN_HEIGHT
            r = int(240 + (250 - 240) * ratio)  # Very light blue to white
            g = int(248 + (255 - 248) * ratio)
            b = int(255)
            color = (r, g, b)
            pygame.draw.line(screen, color, (0, y), (Config.SCREEN_WIDTH, y))

    def draw_completion_stars(self, screen):
        """Draw celebration stars when puzzle is completed."""
        for star in self.completion_stars[:]:  # Copy list to allow removal
            # Update star position
            star['x'] += math.cos(star['angle']) * star['speed']
            star['y'] += math.sin(star['angle']) * star['speed']
            star['life'] -= 0.01
            
            if star['life'] <= 0:
                self.completion_stars.remove(star)
                continue
            
            # Draw star with fading effect
            alpha = star['life']
            size = int(star['original_size'] * alpha)
            brightness = int(255 * alpha)
            color = (brightness, brightness, 100)
            
            if size > 0:
                self.draw_star(screen, star['x'], star['y'], size, color)

    def draw_fancy_border(self, screen, rect, thickness=3, animated=False):
        """Draw a colorful animated border."""
        colors = [
            (100, 200, 255),  # Bright blue
            (255, 100, 150),  # Bright pink  
            (100, 255, 150),  # Bright green
            (255, 255, 100),  # Bright yellow
        ]
        
        for i in range(thickness):
            if animated:
                color_idx = int(self.animation_time * 2 + i) % len(colors)
            else:
                color_idx = i % len(colors)
            color = colors[color_idx]
            pygame.draw.rect(screen, color, rect.inflate(i*2, i*2), 1)

    def draw_button_with_shadow(self, screen, rect, color, border_color, text, font, text_color, animated=False):
        """Draw a button with shadow and fun styling (same as menu)."""
        # Shadow
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=15)
        
        # Main button with rounded corners
        button_color = color
        if animated:
            pulse = abs(math.sin(self.animation_time * 4)) * 30
            button_color = tuple(min(255, int(c + pulse)) for c in color)
        
        pygame.draw.rect(screen, button_color, rect, border_radius=15)
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=15)
        
        # Button text
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

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
        
        # Reset animations
        self.animation_time = 0
        self.completion_stars = []
        
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
            
            if self.map_frame and self.map_frame.handle_zoom(event):
                return
            
            if self.map_frame and self.map_frame.handle_pan(event):
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.map_frame.is_panning:
                    region_id = self.map_frame.detect_click(event.pos)
                    if region_id is not None:
                        self.color_region(region_id, self.selected_color)
            
            if event.type == pygame.KEYDOWN:
                self.handle_keyboard_shortcuts(event)
    
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
            # Generate celebration stars when successfully completed
            self.generate_completion_stars()

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
        self.completion_stars = []
    
    def update(self, dt):
        """Update game state."""
        
        if self.current_state == self.STATE_PLAYING and self.ui:
            self.ui.update(dt)
    
    def render(self):
        """Render the game."""
        if self.current_state == self.STATE_MENU:
            self.menu.draw(self.screen)
            
        elif self.current_state == self.STATE_PLAYING:
            # Draw gradient background
            self.draw_gradient_background(self.screen)
            
            # Draw map frame
            if self.map_frame:
                self.map_frame.draw()
            
            # Draw UI
            if self.ui:
                self.ui.draw(self.screen)
            
            # Draw completion effects
            if self.game_completed:
                self.draw_completion_message()
                if self.puzzle_valid:
                    # Draw celebration stars
                    self.draw_completion_stars(self.screen)
            
            # Draw level name in top-left with enhanced styling
            self.draw_level_name()
    
    def draw_completion_message(self):
        """Draw completion message with enhanced styling."""
        font_large = pygame.font.Font(None, 64)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        if self.puzzle_valid:
            # Success message with celebration
            main_text = "Puzzle Completed Successfully!"
            text_surface = font_large.render(main_text, True, (255, 255, 255))
            bg_color = (50, 200, 50)  # Green for success
            border_color = (100, 255, 100)
        else:
            # Invalid solution message
            main_text = "Oops! Adjacent regions have the same color!"
            text_surface = font_large.render(main_text, True, (255, 255, 255))
            bg_color = (200, 50, 50)  # Red for invalid
            border_color = (255, 100, 100)
        
        text_rect = text_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 80))
        
        # Enhanced background with shadow and rounded corners
        bg_rect = text_rect.inflate(60, 30)
        shadow_rect = bg_rect.copy()
        shadow_rect.x += 6
        shadow_rect.y += 6
        
        # Draw shadow
        pygame.draw.rect(self.screen, (30, 30, 30), shadow_rect, border_radius=20)
        
        # Draw main background with pulsing effect
        if self.puzzle_valid:
            pulse = abs(math.sin(self.animation_time * 3)) * 30
            final_bg_color = tuple(min(255, int(c + pulse)) for c in bg_color)
        else:
            final_bg_color = bg_color
        
        pygame.draw.rect(self.screen, final_bg_color, bg_rect, border_radius=20)
        
        self.screen.blit(text_surface, text_rect)
        
        # Enhanced time display
        elapsed = self.get_elapsed_time()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        if self.puzzle_valid:
            time_text = f"Final Time: {minutes:02d}:{seconds:02d}"
            time_color = (255, 255, 100)  # Gold color for completion time
        else:
            time_text = f"Current Time: {minutes:02d}:{seconds:02d}"
            time_color = (255, 255, 255)
        
        time_surface = font_medium.render(time_text, True, time_color)
        time_rect = time_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 140))
        
        # Time background
        time_bg_rect = time_rect.inflate(40, 20)
        pygame.draw.rect(self.screen, (50, 50, 50, 128), time_bg_rect, border_radius=15)
        self.screen.blit(time_surface, time_rect)
        
        # Enhanced message with fun styling
        if self.puzzle_valid:
            congrats_text = "Amazing! You solved it perfectly!"
            msg_color = (255, 255, 100)
        else:
            congrats_text = "Keep trying! Change colors to fix conflicts"
            msg_color = (255, 200, 200)
        
        msg_surface = font_small.render(congrats_text, True, msg_color)
        msg_rect = msg_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 190))
        
        # Message background
        msg_bg_rect = msg_rect.inflate(30, 15)
        pygame.draw.rect(self.screen, (30, 30, 30, 100), msg_bg_rect, border_radius=10)
        self.screen.blit(msg_surface, msg_rect)
    
    def draw_level_name(self):
        """Draw the current level name with enhanced styling."""
        if self.current_level:
            font = pygame.font.Font(None, 42)
            level_text = f"{self.current_level['name']}"
            text_surface = font.render(level_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(topleft=(30, 30))
            
            # Enhanced background with shadow
            bg_rect = text_rect.inflate(30, 20)
            shadow_rect = bg_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            
            # Draw shadow
            pygame.draw.rect(self.screen, (30, 30, 30), shadow_rect, border_radius=15)
            
            self.screen.blit(text_surface, text_rect)
    
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
        # Clear celebration effects
        self.completion_stars = []
        
        # Check completion state again
        if self.are_all_regions_colored():
            self.check_completion()
        else:
            self.game_completed = False
            self.puzzle_valid = False

    def handle_keyboard_shortcuts(self, event):
        """Handle keyboard shortcuts for zooming and other actions."""
        if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            # Zoom in with + or =
            if self.map_frame:
                self.map_frame.zoom_level = min(
                    self.map_frame.zoom_level + self.map_frame.zoom_speed,
                    self.map_frame.max_zoom
                )
        elif event.key == pygame.K_MINUS:
            # Zoom out with -
            if self.map_frame:
                self.map_frame.zoom_level = max(
                    self.map_frame.zoom_level - self.map_frame.zoom_speed,
                    self.map_frame.min_zoom
                )
        elif event.key == pygame.K_0:
            # Reset view with 0
            if self.map_frame:
                self.map_frame.reset_view()
        elif event.key == pygame.K_SPACE:
            # Center map with spacebar
            if self.map_frame:
                self.map_frame.center_map()