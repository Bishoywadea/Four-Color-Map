# main.py
import pygame
import sys

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
        pygame.display.set_caption(("Four Color Map Puzzle"))

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
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Four Color Map Puzzle")
        
        # Set up font and text
        font = pygame.font.Font(None, 36)
        text = font.render("Hello, Four Color Map!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(400, 300))
        
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            # Draw text
            screen.blit(text, text_rect)
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    game_instance = main(journal=False)
    game_instance.run()