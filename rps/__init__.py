"""Rock Paper Scissors, a small pygame game.

The package is layered so each piece can be read and tested on its own:

* :mod:`rps.config` - tunable constants, no logic.
* :mod:`rps.rules`  - moves, outcomes and rounds, with no pygame dependency.
* :mod:`rps.audio`  - the outcome-to-sound mapping.
* :mod:`rps.ui`     - reusable widgets that draw onto a surface.
* :mod:`rps.scenes` - one class per screen of the game.
* :mod:`rps.app`    - the window and the main loop.

Run the game with ``python rock_paper_scissors.py`` from the project root.
"""

from .app import Game

__all__ = ['Game']
