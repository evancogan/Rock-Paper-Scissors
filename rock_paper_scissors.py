"""Launch Rock Paper Scissors.

The game itself lives in the :mod:`rps` package; this module is just the
entry point, so ``python rock_paper_scissors.py`` keeps working.
"""

from rps import Game


def main():
    """Create the game and run it until the player quits."""
    Game().run()


if __name__ == '__main__':
    main()
