# main.py
import pygame
import sys
from logic.game_manager import GameManager
from view.config import Config
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gettext import gettext as _

class main:
    def __init__(self, journal=True):
        self.journal = journal
        self.running = True
        self.canvas = None
        self.score = [0, 0]
        self.show_help = False
        self.game = None
        self.help_pos = None 
        self.question_text = None 
        self.close_text = None 
        self.help_text = None 


    def set_canvas(self, canvas):
        self.canvas = canvas
        pygame.display.set_caption(_("Four Color Map Puzzle"))

    def write_file(self, file_path):
        pass

    def read_file(self, file_path):
        pass

    def quit(self):
        self.running = False
    
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode(event.size, pygame.RESIZABLE)
                break
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.help_pos and self.help_pos.collidepoint(pygame.mouse.get_pos()):
                    self.show_help = not self.show_help
                elif self.show_help:
                    # If help is showing, clicking anywhere else should close it
                    self.show_help = False
                else:
                    # Pass event to game manager
                    if self.game:
                        self.game.handle_event(event)
            else:
                # Pass other events to game manager
                if self.game:
                    self.game.handle_event(event)
    
    def draw_help(self, screen):
        # Draw the help button
        pygame.draw.circle(
            screen,
            Config.COLORS['UI_BACKGROUND'],
            self.help_pos.center,
            40,
        )
        
        if self.show_help:
            # Calculate size based on text
            padding = 20
            spacing = 10
            total_height = sum(text.get_height() + spacing for text in self.help_text) + padding * 2
            max_width = max(text.get_width() for text in self.help_text) + padding * 2
            # Draw the help panel background
            help_panel = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
            help_panel.fill((80, 80, 120, 230))  # Background color
            
            # Draw border
            pygame.draw.rect(
                help_panel,
                Config.COLORS['BORDER'],
                (0, 0, max_width, total_height),
                3
            )
            
            # Position the panel centered on screen
            panel_x = (Config.SCREEN_WIDTH - max_width) // 2
            panel_y = (Config.SCREEN_HEIGHT - total_height) // 2
            screen.blit(help_panel, (panel_x, panel_y))
            
            # Draw help text
            y_offset = panel_y + padding
            for text in self.help_text:
                text_x = panel_x + (max_width - text.get_width()) // 2
                screen.blit(text, (text_x, y_offset))
                y_offset += text.get_height() + spacing
            
            q_x = self.help_pos.centerx - self.question_text.get_width() // 2
            q_y = self.help_pos.centery - self.question_text.get_height() // 2
            screen.blit(self.close_text, (q_x, q_y))
        else:
            # Draw the question mark on help button
            q_x = self.help_pos.centerx - self.question_text.get_width() // 2
            q_y = self.help_pos.centery - self.question_text.get_height() // 2
            screen.blit(self.question_text, (q_x, q_y))


    def run(self):
        # Initialize pygame
        pygame.init()

        # Initialize fonts and help content
        font = pygame.font.Font(None, 64)
        self.question_text = font.render("?", True, Config.COLORS['BORDER'])
        self.close_text = font.render("X", True, Config.COLORS['BORDER'])
        self.help_text = [
            font.render(line, True, (255, 255, 255))  # White text
            for line in [
                _("Four Color Map Puzzle Rules:"),
                _("1. Color each region using one of four colors."),
                _("2. Adjacent regions cannot share the same color."),
                _("3. Use the color buttons to select a color."),
                _("4. Click on a region to apply the selected color."),
                _("5. Complete the map with no adjacent conflicts.")
            ]
        ]
        
        self.help_pos = pygame.Rect(
            (2 * Config.SCREEN_WIDTH ),
            (Config.SCREEN_HEIGHT * 0.1),
            80,
            80,
        )
        
        # Initialize the game
        self.game = GameManager()
        
        # Set canvas focus if available
        if self.canvas is not None:
            self.canvas.grab_focus()
        
        # Main game loop
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle GTK events for Sugar integration
            if self.journal:
                # Pump GTK messages
                while Gtk.events_pending():
                    Gtk.main_iteration()
            
            dt = clock.tick(Config.FPS)
            
            # Handle pygame events
            self.check_events()
            
            # Update game state
            if self.game:
                self.game.update(dt)
                
                # Render everything
                self.game.render()
                self.draw_help(pygame.display.get_surface())
                
            pygame.display.flip()
        
        # Clean up
        pygame.display.quit()
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    game_instance = main(journal=False)
    game_instance.run()