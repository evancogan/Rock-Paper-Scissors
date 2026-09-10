"""Sound effects for round outcomes."""

from pathlib import Path

import pygame

from .rules import Outcome

# Audio lives alongside the game rather than inside the package, so resolve it
# from this file's location. Launching from another working directory then
# still finds the files.
ASSET_DIR = Path(__file__).resolve().parent.parent

#: Which effect plays for each outcome. Every Outcome must appear here;
#: SoundBoard checks that on construction.
OUTCOME_TRACKS = {
    Outcome.PLAYER_WINS: 'ding.mp3',
    Outcome.COMPUTER_WINS: 'bong.mp3',
    Outcome.TIE: 'wow.mp3',
}


class SoundBoard:
    """Plays one short effect per round outcome.

    Wraps ``pygame.mixer.music``, which allows a single track at a time: each
    new outcome interrupts the previous one rather than layering over it.
    """

    def __init__(self, tracks=None):
        """Initialise the mixer and validate the outcome-to-file mapping.

        Args:
            tracks: Optional override mapping :class:`Outcome` to filename,
                mainly so tests can substitute silence.

        Raises:
            ValueError: If any outcome has no sound assigned.
        """
        pygame.mixer.init()
        self._tracks = dict(OUTCOME_TRACKS if tracks is None else tracks)
        missing = set(Outcome) - set(self._tracks)
        if missing:
            raise ValueError(f'no sound assigned for: {sorted(m.name for m in missing)}')

    def path_for(self, outcome):
        """Return the full path to the effect for ``outcome``."""
        return ASSET_DIR / self._tracks[outcome]

    def play(self, outcome):
        """Play the effect for ``outcome``, replacing anything already playing."""
        pygame.mixer.music.load(str(self.path_for(outcome)))
        pygame.mixer.music.play()
