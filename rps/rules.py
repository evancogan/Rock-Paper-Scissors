"""The rules of rock paper scissors.

Deliberately free of pygame: this module knows what beats what and nothing
about drawing, sound or input. That keeps the rules testable on their own and
stops the display strings from leaking into the game logic.
"""

import random
from enum import Enum


class Move(Enum):
    """One of the three throws a player can make."""

    ROCK = 'rock'
    PAPER = 'paper'
    SCISSORS = 'scissors'

    @property
    def label(self):
        """The move's name as shown to the player, e.g. ``'Rock'``."""
        return self.value.capitalize()

    def beats(self, other):
        """Return True if this move defeats ``other``."""
        return _DEFEATS[self] is other

    @classmethod
    def random(cls):
        """Pick a move uniformly at random, as the computer opponent does."""
        return random.choice(list(cls))


# Kept beside the enum rather than inside it: an Enum body would treat these
# as extra members. Each move maps to the single move it defeats.
_DEFEATS = {
    Move.ROCK: Move.SCISSORS,
    Move.SCISSORS: Move.PAPER,
    Move.PAPER: Move.ROCK,
}


class Outcome(Enum):
    """The result of a round, from the player's point of view.

    The values double as the text shown on the result line, so the display
    wording lives in exactly one place.
    """

    PLAYER_WINS = 'Player wins'
    COMPUTER_WINS = 'Computer wins'
    TIE = 'Tie'

    @property
    def label(self):
        """The outcome as shown to the player."""
        return self.value

    @property
    def costs_a_life(self):
        """True if this outcome should take one of the player's lives."""
        return self is Outcome.COMPUTER_WINS

    @property
    def restores_a_life(self):
        """True if this outcome should give a spent life back."""
        return self is Outcome.PLAYER_WINS


def resolve(player_move, computer_move):
    """Return the :class:`Outcome` of ``player_move`` against ``computer_move``."""
    if player_move is computer_move:
        return Outcome.TIE
    if player_move.beats(computer_move):
        return Outcome.PLAYER_WINS
    return Outcome.COMPUTER_WINS


class Round:
    """One settled round: what each side threw, and who won.

    Holding these together means the display never has to re-derive the
    outcome, and there is no window in which a move is recorded but the
    result is not.
    """

    def __init__(self, player_move, computer_move):
        self.player_move = player_move
        self.computer_move = computer_move
        self.outcome = resolve(player_move, computer_move)

    @classmethod
    def against_computer(cls, player_move):
        """Play ``player_move`` against a fresh random computer move."""
        return cls(player_move, Move.random())

    def summary_lines(self):
        """The three lines shown on the board, top to bottom."""
        return (
            f'Player: {self.player_move.value}',
            f'Computer: {self.computer_move.value}',
            f'Result: {self.outcome.label}',
        )

    def __repr__(self):
        return (f'Round({self.player_move.name} vs {self.computer_move.name}'
                f' -> {self.outcome.name})')
