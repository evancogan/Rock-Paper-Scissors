"""Launch Rock Paper Scissors.

The game itself lives in the :mod:`rps` package; this module is just the
entry point, so ``python rock_paper_scissors.py`` keeps working.
"""

import argparse

from rps import Game
from rps import config


def parse_args(argv=None):
    """Read the command line, returning the parsed options."""
    parser = argparse.ArgumentParser(description='Play Rock Paper Scissors.')
    parser.add_argument(
        '--debug',
        action='store_true',
        help=('show the developer overlay: what each side threw and who won. '
              f'Can also be toggled in game with {config.DEBUG_TOGGLE_KEY.upper()}.'),
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Create the game and run it until the player quits."""
    Game(debug=parse_args(argv).debug).run()


if __name__ == '__main__':
    main()
