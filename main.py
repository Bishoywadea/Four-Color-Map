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
            else:
                # Pass event to game manager
                if self.game:
                    self.game.handle_event(event)

    def run(self):
        # Initialize pygame
        pygame.init()
        
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