"""The game's screens.

Each screen is a :class:`Scene` that handles its own input, timing and
drawing. The main loop just forwards to whichever scene is active, so adding
a screen means adding a class rather than another branch in three separate
``if state == ...`` chains.
"""

import pygame

from . import config
from .rules import Move, Outcome, Round
from .ui import Button, LivesMeter, draw_backed_text, draw_centered_text


class Scene:
    """Base class for a screen of the game.

    Subclasses override the three hooks the main loop calls each frame. The
    current time in milliseconds is passed in rather than read from pygame
    inside the scene, which keeps timing deterministic under test.
    """

    def __init__(self, game):
        self.game = game

    def on_enter(self, ticks):
        """Called once when this scene becomes the active one."""

    def handle_event(self, event, ticks):
        """Respond to a single pygame event."""

    def update(self, ticks):
        """Advance any time-based behaviour."""

    def draw(self, surface, ticks):
        """Render the scene onto ``surface``."""
        raise NotImplementedError


class MenuScene(Scene):
    """The title screen, offering Play and Quit."""

    def __init__(self, game):
        super().__init__(game)
        font = game.fonts.body
        self.play_button = Button(config.PLAY_BUTTON_RECT, 'Play', font)
        self.quit_button = Button(config.QUIT_BUTTON_RECT, 'Quit', font)

    def handle_event(self, event, ticks):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.play_button.contains(event.pos):
                self.game.start_new_game()
            elif self.quit_button.contains(event.pos):
                self.game.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.game.start_new_game()
            elif event.key == pygame.K_ESCAPE:
                self.game.quit()

    def draw(self, surface, ticks):
        self.game.background.draw(surface, ticks)
        draw_centered_text(surface, config.WINDOW_TITLE, config.MENU_TITLE_CENTER,
                           self.game.fonts.title, config.WHITE)
        mouse_pos = pygame.mouse.get_pos()
        self.play_button.draw(surface, mouse_pos)
        self.quit_button.draw(surface, mouse_pos)


class PlayScene(Scene):
    """The board: three choices, the last round's result, the lives meter and
    the tally of rounds won.

    A fresh instance is built for every new game, so the win count and the
    lives both start over without any explicit reset.
    """

    def __init__(self, game):
        super().__init__(game)
        font = game.fonts.body
        self.lives = LivesMeter(font)
        self.round = None
        self.wins = 0
        self.back_button = Button(config.BACK_BUTTON_RECT, 'Menu', font)
        width, height = config.CHOICE_BUTTON_SIZE
        self.choice_buttons = {
            move: Button((left, config.CHOICE_BUTTON_TOP, width, height),
                         move.label, font, growth=config.CHOICE_BUTTON_GROWTH)
            for move, left in zip(Move, config.CHOICE_BUTTON_LEFTS)
        }

    # --- input -------------------------------------------------------------

    def handle_event(self, event, ticks):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._press_choice_at(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.back_button.contains(event.pos):
                self.game.open_menu()
            elif self._pressed_move is not None:
                self._settle_round()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.open_menu()

    @property
    def _pressed_move(self):
        """The move whose button is currently held down, or None."""
        for move, button in self.choice_buttons.items():
            if button.pressed:
                return move
        return None

    def _press_choice_at(self, pos):
        """Hold down whichever choice button is under ``pos``, if any."""
        for button in self.choice_buttons.values():
            if button.contains(pos):
                button.pressed = True
                return

    def _release_buttons(self):
        for button in self.choice_buttons.values():
            button.pressed = False

    def _settle_round(self):
        """Play the held move against the computer and apply the result.

        Only reached when a choice button is actually held, so a stray click
        on the background cannot re-roll the round.
        """
        player_move = self._pressed_move
        self._release_buttons()
        self.round = Round.against_computer(player_move)
        if self.round.outcome is Outcome.PLAYER_WINS:
            self.wins += 1
        self.game.sounds.play(self.round.outcome)
        if self.lives.apply(self.round.outcome):
            self.game.end_game(self)

    # --- drawing -----------------------------------------------------------

    def draw(self, surface, ticks):
        self.game.background.draw(surface, ticks)
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.draw(surface, mouse_pos)
        self.lives.draw(surface)
        draw_backed_text(surface, config.ROUNDS_WON_LABEL.format(count=self.wins),
                         config.ROUNDS_WON_POS, self.game.fonts.body)
        if self.round is not None:
            for line, top in zip(self.round.summary_lines(), config.ROUND_TEXT_TOPS):
                draw_backed_text(surface, line, (config.ROUND_TEXT_X, top),
                                 self.game.fonts.body)
        for button in self.choice_buttons.values():
            button.draw(surface, mouse_pos)


class GameOverScene(Scene):
    """The darkness closing over a finished game.

    The board that was being played stays visible underneath and is drawn
    first each frame, so the player watches the dark swallow the losing hand
    instead of cutting away from it.
    """

    def __init__(self, game, board):
        super().__init__(game)
        self.board = board
        self.started_at = 0
        self._shade = pygame.Surface(config.SCREEN_SIZE)
        self._shade.fill(config.BLACK)

    def on_enter(self, ticks):
        self.started_at = ticks

    def fade_progress(self, ticks):
        """How far the fade has come: 0.0 at the moment of death, 1.0 at full dark."""
        elapsed = ticks - self.started_at
        return min(1.0, max(0.0, elapsed / config.GAME_OVER_FADE_MS))

    def finished_fading(self, ticks):
        """True once the screen has reached full darkness."""
        return self.fade_progress(ticks) >= 1.0

    def handle_event(self, event, ticks):
        # Input is ignored until the fade has played out, so the mouse release
        # that spent the last life cannot dismiss the screen it just triggered.
        if not self.finished_fading(ticks):
            return
        if event.type in (pygame.MOUSEBUTTONUP, pygame.KEYDOWN):
            self.game.open_menu()

    def update(self, ticks):
        if ticks - self.started_at >= config.GAME_OVER_FADE_MS + config.GAME_OVER_HOLD_MS:
            self.game.open_menu()

    def draw(self, surface, ticks):
        self.board.draw(surface, ticks)
        fade = self.fade_progress(ticks)
        # Squared easing: barely moves at first, then rushes in at the end.
        self._shade.set_alpha(round(config.GAME_OVER_SHADE * fade * fade))
        surface.blit(self._shade, (0, 0))

        # The words surface only over the back of the fade, once it is dim.
        delay = config.GAME_OVER_TEXT_DELAY
        text_fade = max(0.0, (fade - delay) / (1 - delay))
        if text_fade > 0:
            draw_centered_text(surface, config.GAME_OVER_TEXT, config.GAME_OVER_TEXT_CENTER,
                               self.game.fonts.title, config.GAME_OVER_COLOR,
                               alpha=round(255 * text_fade))
        if self.finished_fading(ticks):
            draw_centered_text(surface, config.GAME_OVER_HINT, config.GAME_OVER_HINT_CENTER,
                               self.game.fonts.body, config.WHITE,
                               alpha=config.GAME_OVER_HINT_ALPHA)
