import math
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up display variables
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Rock Paper Scissors')

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_HOVER = (215, 215, 215)

# The background is a vertical gradient whose two ends drift between these
# blues and back again, once every GRADIENT_PERIOD_MS.
GRADIENT_TOP = ((12, 28, 84), (24, 74, 150))
GRADIENT_BOTTOM = ((36, 116, 194), (10, 52, 122))
GRADIENT_PERIOD_MS = 30000
GRADIENT_BANDS = 256  # rows in the source strip, smoothscaled up to the screen

# Set up fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Screens the game can be on
MENU = 'menu'
GAME = 'game'


def lerp_color(start, end, amount):
    return tuple(round(start[i] + (end[i] - start[i]) * amount) for i in range(3))


class RockPaperScissors:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.state = MENU
        self.player_choice = None
        self.computer_choice = None
        self.button_rects = {
            'rock': pygame.Rect(100, 300, 100, 50),
            'paper': pygame.Rect(300, 300, 100, 50),
            'scissors': pygame.Rect(500, 300, 100, 50)
        }
        self.button_pressing = {'rock': False, 'paper': False, 'scissors': False}
        self.menu_button_rects = {
            'play': pygame.Rect(300, 300, 200, 60),
            'quit': pygame.Rect(300, 390, 200, 60)
        }
        self.back_button_rect = pygame.Rect(630, 30, 140, 50)
        self.gradient_surface = None
        self.gradient_ends = None
        pygame.mixer.init()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def start_game(self):
        self.state = GAME
        self.reset_round()

    def open_menu(self):
        self.state = MENU
        self.reset_round()

    def reset_round(self):
        self.player_choice = None
        self.computer_choice = None
        for choice in self.button_pressing:
            self.button_pressing[choice] = False

    def draw_text(self, text, x, y):
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(topleft=(x, y))
        pygame.draw.rect(self.screen, (0, 0, 0, 128), text_rect)  # black background
        self.screen.blit(text_surface, (x, y))

    def gradient_ends_at(self, ticks):
        # Cosine easing so the drift turns around smoothly instead of snapping
        # back to the start of the cycle.
        phase = (1 - math.cos(2 * math.pi * ticks / GRADIENT_PERIOD_MS)) / 2
        return (lerp_color(GRADIENT_TOP[0], GRADIENT_TOP[1], phase),
                lerp_color(GRADIENT_BOTTOM[0], GRADIENT_BOTTOM[1], phase))

    def draw_background(self):
        ends = self.gradient_ends_at(pygame.time.get_ticks())
        # The colors move slowly enough that most frames can reuse the last
        # surface; only rebuild once the rounded endpoints actually change.
        if ends != self.gradient_ends:
            self.gradient_ends = ends
            top, bottom = ends
            strip = pygame.Surface((1, GRADIENT_BANDS))
            for y in range(GRADIENT_BANDS):
                strip.set_at((0, y), lerp_color(top, bottom, y / (GRADIENT_BANDS - 1)))
            self.gradient_surface = pygame.transform.smoothscale(strip, (screen_width, screen_height))
        self.screen.blit(self.gradient_surface, (0, 0))

    def draw_centered_text(self, text, rect, color, text_font=font):
        text_surface = text_font.render(text, True, color)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def draw_menu_button(self, rect, label):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, BUTTON_HOVER if hovered else WHITE, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        self.draw_centered_text(label, rect, BLACK)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif self.state == MENU:
                self.handle_menu_event(event)
            else:
                self.handle_game_event(event)

    def handle_menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.menu_button_rects['play'].collidepoint(event.pos):
                self.start_game()
            elif self.menu_button_rects['quit'].collidepoint(event.pos):
                self.quit_game()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.quit_game()

    def handle_game_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
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
            if self.back_button_rect.collidepoint(event.pos):
                self.open_menu()
            elif any(self.button_pressing.values()):
                # only settle a round if this release follows a press on a choice
                self.button_pressing['rock'] = False
                self.button_pressing['paper'] = False
                self.button_pressing['scissors'] = False
                self.computer_choice = random.choice(['rock', 'paper', 'scissors'])
                self.play_effects(self.determine_winner())
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.open_menu()

    def determine_winner(self):
        if self.player_choice is None or self.computer_choice is None:
            return ''
        elif self.player_choice == self.computer_choice:
            return 'Tie'
        elif (self.player_choice == 'rock' and self.computer_choice == 'scissors') or (self.player_choice == 'scissors' and self.computer_choice == 'paper') or (self.player_choice == 'paper' and self.computer_choice == 'rock'):
            return 'Player wins'
        else:
            return 'Computer wins'

    def play_effects(self, winner):
        if winner == 'Player wins':
            pygame.mixer.music.load('ding.mp3')
            pygame.mixer.music.play()
        elif winner == 'Computer wins':
            pygame.mixer.music.load('bong.mp3')
            pygame.mixer.music.play()

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

    def draw_menu(self):
        self.draw_background()
        title_surface = title_font.render('Rock Paper Scissors', True, WHITE)
        self.screen.blit(title_surface, title_surface.get_rect(center=(screen_width // 2, 160)))
        self.draw_menu_button(self.menu_button_rects['play'], 'Play')
        self.draw_menu_button(self.menu_button_rects['quit'], 'Quit')

    def draw_game(self):
        self.draw_background()
        self.draw_menu_button(self.back_button_rect, 'Menu')
        if self.player_choice is not None and self.computer_choice is not None:
            self.draw_text(f'Player: {self.player_choice}', 100, 100)
            self.draw_text(f'Computer: {self.computer_choice}', 100, 150)
            self.draw_text(f'Result: {self.determine_winner()}', 100, 200)
        self.draw_buttons()

    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        else:
            self.draw_game()
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(60)


if __name__ == '__main__':
    game = RockPaperScissors()
    game.run()
