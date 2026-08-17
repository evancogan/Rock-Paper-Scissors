import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up display variables
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up font
font = pygame.font.Font(None, 36)

class RockPaperScissors:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.player_choice = None
        self.computer_choice = None
        self.button_rects = {}
        self.button_pressing = {'rock': False, 'paper': False, 'scissors': False}

    def draw_text(self, text, x, y):
        text_surface = font.render(text, True, WHITE)
        self.screen.blit(text_surface, (x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_rects['rock'].collidepoint(event.pos):
                    self.player_choice = 'rock'
                    self.button_pressing['rock'] = True
                elif self.button_rects['paper'].collidepoint(event.pos):
                    self.player_choice = 'paper'
                    self.button_pressing['paper'] = True
                elif self.button_rects['scissors'].collidepoint(event.pos):
                    self.player_choice = 'scissors'
                    self.button_pressing['scissors'] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.button_pressing['rock'] = False
                self.button_pressing['paper'] = False
                self.button_pressing['scissors'] = False
                if random.choice([True, False]):
                    self.computer_choice = random.choice(['rock', 'paper', 'scissors'])

    def determine_winner(self):
        if self.player_choice is None or self.computer_choice is None:
            return ''
        elif self.player_choice == self.computer_choice:
            return 'Tie'
        elif (self.player_choice == 'rock' and self.computer_choice == 'scissors') or (self.player_choice == 'scissors' and self.computer_choice == 'paper') or (self.player_choice == 'paper' and self.computer_choice == 'rock'):
            pygame.mixer.init()
            pygame.mixer.music.load('ding.mp3')
            pygame.mixer.music.play()
            return 'Player wins'
        else:
            return 'Computer wins'

    def draw_buttons(self):
        if self.button_pressing['rock']:
            self.button_rects['rock'] = pygame.Rect(100, 300, 120, 60)
            pygame.draw.rect(self.screen, WHITE, self.button_rects['rock'])
        else:
            self.button_rects['rock'] = pygame.Rect(100, 300, 100, 50)
            pygame.draw.rect(self.screen, WHITE, self.button_rects['rock'])

        if self.button_pressing['paper']:
            self.button_rects['paper'] = pygame.Rect(300, 300, 120, 60)
            pygame.draw.rect(self.screen, WHITE, self.button_rects['paper'])
        else:
            self.button_rects['paper'] = pygame.Rect(300, 300, 100, 50)
            pygame.draw.rect(self.screen, WHITE, self.button_rects['paper'])

        if self.button_pressing['scissors']:
            self.button_rects['scissors'] = pygame.Rect(500, 300, 120, 60)
            pygame.draw.rect(self.screen, WHITE, self.button_rects['scissors'])
        else:
            self.button_rects['scissors'] = pygame.Rect(500, 300, 100, 50)
            pygame.draw.rect(self.screen, WHITE, self.button_rects['scissors'])

        font = pygame.font.Font(None, 36)
        text_surface = font.render('Rock', True, BLACK)
        self.screen.blit(text_surface, (self.button_rects['rock'].centerx - 50, self.button_rects['rock'].centery))
        text_surface = font.render('Paper', True, BLACK)
        self.screen.blit(text_surface, (self.button_rects['paper'].centerx - 50, self.button_rects['paper'].centery))
        text_surface = font.render('Scissors', True, BLACK)
        self.screen.blit(text_surface, (self.button_rects['scissors'].centerx - 50, self.button_rects['scissors'].centery))
        pygame.display.flip()

    def draw(self):
        self.screen.fill((0, 255, 255))
        if self.player_choice is not None and self.computer_choice is not None:
            self.draw_text(f'Player: {self.player_choice}', 100, 100)
            self.draw_text(f'Computer: {self.computer_choice}', 100, 150)
            self.draw_text(f'Result: {self.determine_winner()}', 100, 200)
        self.draw_buttons()

    def run(self):
        running = True
        self.button_rects = {
            'rock': pygame.Rect(100, 300, 100, 50),
            'paper': pygame.Rect(300, 300, 100, 50),
            'scissors': pygame.Rect(500, 300, 100, 50)
        }
        while running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    game = RockPaperScissors()
    game.run()



