"""The application shell: window, main loop and scene switching."""

import pygame

from . import config
from .audio import SoundBoard
from .scenes import GameOverScene, MenuScene, PlayScene
from .ui import Fonts, GradientBackground, draw_backed_text


class Game:
    """Owns the window, the clock, the shared assets and the active scene.

    Scenes reach back through this object for anything shared - the fonts,
    the drifting background, the sound board - and call its transition
    methods rather than assigning a state flag.
    """

    def __init__(self, debug=config.DEBUG_DEFAULT):
        """Set up the window and shared assets.

        Args:
            debug: Start with the developer overlay visible. It can also be
                toggled at any time with the key named by
                ``config.DEBUG_TOGGLE_KEY``.
        """
        pygame.init()
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE)
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.fonts = Fonts()
        self.background = GradientBackground()
        self.sounds = SoundBoard()
        self.debug = debug
        self._debug_key = pygame.key.key_code(config.DEBUG_TOGGLE_KEY)
        self.running = True
        self.scene = None
        self.open_menu()

    def toggle_debug(self):
        """Flip the developer overlay on or off."""
        self.debug = not self.debug

    # --- scene transitions -------------------------------------------------

    def go_to(self, scene):
        """Make ``scene`` active and let it initialise itself."""
        self.scene = scene
        scene.on_enter(pygame.time.get_ticks())

    def open_menu(self):
        """Return to the title screen, abandoning any game in progress."""
        self.go_to(MenuScene(self))

    def start_new_game(self):
        """Begin a fresh game with a full set of lives."""
        self.go_to(PlayScene(self))

    def end_game(self, board):
        """Fade out ``board`` after its last life is spent."""
        self.go_to(GameOverScene(self, board))

    def quit(self):
        """Ask the main loop to stop after the current frame."""
        self.running = False

    # --- main loop ---------------------------------------------------------

    def run(self):
        """Run until the player quits, then shut pygame down cleanly."""
        try:
            while self.running:
                ticks = pygame.time.get_ticks()
                self._pump_events(ticks)
                self.scene.update(ticks)
                self.scene.draw(self.screen, ticks)
                self._draw_debug_badge()
                pygame.display.flip()
                self.clock.tick(config.FRAMES_PER_SECOND)
        finally:
            pygame.quit()

    def _draw_debug_badge(self):
        """Mark the screen while debug is on, so the mode is never a mystery.

        Drawn over every scene rather than inside one, because the overlay is
        a property of the app and stays on across screen changes.
        """
        if self.debug:
            draw_backed_text(self.screen, config.DEBUG_BADGE,
                             config.DEBUG_BADGE_POS, self.fonts.body)

    def _pump_events(self, ticks):
        """Forward this frame's events to the active scene."""
        # Drains the event queue each frame; QUIT and debug are global, other events go to the scene.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN and event.key == self._debug_key:
                self.toggle_debug()
            else:
                self.scene.handle_event(event, ticks)
