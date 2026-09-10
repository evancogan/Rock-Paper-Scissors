"""The application shell: window, main loop and scene switching."""

import pygame

from . import config
from .audio import SoundBoard
from .scenes import GameOverScene, MenuScene, PlayScene
from .ui import Fonts, GradientBackground


class Game:
    """Owns the window, the clock, the shared assets and the active scene.

    Scenes reach back through this object for anything shared - the fonts,
    the drifting background, the sound board - and call its transition
    methods rather than assigning a state flag.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE)
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.fonts = Fonts()
        self.background = GradientBackground()
        self.sounds = SoundBoard()
        self.running = True
        self.scene = None
        self.open_menu()

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
                pygame.display.flip()
                self.clock.tick(config.FRAMES_PER_SECOND)
        finally:
            pygame.quit()

    def _pump_events(self, ticks):
        """Forward this frame's events to the active scene."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            else:
                self.scene.handle_event(event, ticks)
