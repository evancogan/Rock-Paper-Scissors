"""Tunable constants for the game.

This module holds pure data only - no pygame calls and no imports from the
rest of the package - so it can be read before pygame is initialised and
imported by tests that never open a window. Change the feel of the game here
rather than hunting through the drawing code.
"""

# --- Display ---------------------------------------------------------------

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
WINDOW_TITLE = 'Rock Paper Scissors'
FRAMES_PER_SECOND = 60

# --- Palette ---------------------------------------------------------------

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BUTTON_FACE = WHITE
BUTTON_HOVER = (215, 215, 215)
BUTTON_BORDER = BLACK
BUTTON_LABEL = BLACK
BUTTON_BORDER_WIDTH = 2

TEXT_COLOR = WHITE
TEXT_BACKING = BLACK  # opaque block behind body text, to lift it off the gradient

# --- Fonts -----------------------------------------------------------------

BODY_FONT_SIZE = 36
TITLE_FONT_SIZE = 72

# --- Background gradient ---------------------------------------------------
# Each end of the vertical gradient drifts between its two blues and back
# again, once every GRADIENT_PERIOD_MS.

GRADIENT_TOP = ((12, 28, 84), (24, 74, 150))
GRADIENT_BOTTOM = ((36, 116, 194), (10, 52, 122))
GRADIENT_PERIOD_MS = 30000
GRADIENT_BANDS = 256  # rows in the source strip, smoothscaled up to the screen

# --- Lives -----------------------------------------------------------------

STARTING_LIVES = 3
LIFE_PIP_COLOR = (222, 74, 74)
LIFE_SPENT_COLOR = (52, 58, 80)
LIFE_PIP_SIZE = 24
LIFE_PIP_SPACING = 34
LIFE_PIP_ORIGIN = (200, 44)
LIVES_LABEL_POS = (100, 40)

# --- Rounds won ------------------------------------------------------------

ROUNDS_WON_LABEL = 'Rounds won: {count}'
ROUNDS_WON_POS = (330, 40)  # top row, clear of the pips (end 292) and Menu (start 630)

# --- Countdown -------------------------------------------------------------
# After a choice is made, these labels bounce through one at a time and the
# round is revealed as the last one ends. The font size is set so the widest
# label still fits the screen at the peak of its pop: 'SCISSORS' is 363px at
# size 100, or 690px scaled by 1 + COUNTDOWN_POP.

COUNTDOWN_LABELS = ('ROCK', 'PAPER', 'SCISSORS', 'SHOOT!')
COUNTDOWN_STEP_MS = 450  # how long each label holds the screen
COUNTDOWN_FONT_SIZE = 100
COUNTDOWN_COLOR = WHITE
COUNTDOWN_CENTER = (SCREEN_WIDTH // 2, 190)
COUNTDOWN_POP = 0.9  # extra size at the instant a label appears, as a fraction
COUNTDOWN_HOPS = 2  # how many times a label bounces before settling
COUNTDOWN_HOP_HEIGHT = 26  # pixels of lift on the first hop
COUNTDOWN_FADE_FROM = 0.72  # fraction of a beat before the label fades out

# --- Game over -------------------------------------------------------------

GAME_OVER_TEXT = 'GAME OVER'
GAME_OVER_HINT = 'Returning to the menu...'
GAME_OVER_COLOR = (188, 26, 26)
GAME_OVER_SHADE = 238  # how black the overlay finally gets, out of 255
GAME_OVER_FADE_MS = 2600  # time for the dark to close over the board
GAME_OVER_HOLD_MS = 1600  # beat at full dark before the menu comes back
GAME_OVER_TEXT_DELAY = 0.45  # fraction of the fade to wait before the words show
GAME_OVER_HINT_ALPHA = 160
GAME_OVER_TEXT_CENTER = (SCREEN_WIDTH // 2, 264)
GAME_OVER_HINT_CENTER = (SCREEN_WIDTH // 2, 410)

# --- Layout ----------------------------------------------------------------

MENU_TITLE_CENTER = (SCREEN_WIDTH // 2, 160)
PLAY_BUTTON_RECT = (300, 300, 200, 60)
QUIT_BUTTON_RECT = (300, 390, 200, 60)
BACK_BUTTON_RECT = (630, 30, 140, 50)

CHOICE_BUTTON_SIZE = (130, 50)  # wide enough for 'Scissors' at BODY_FONT_SIZE
CHOICE_BUTTON_TOP = 300
CHOICE_BUTTON_LEFTS = (100, 300, 500)
CHOICE_BUTTON_GROWTH = (20, 10)  # how much a button swells while held down

ROUND_TEXT_X = 100
ROUND_TEXT_TOPS = (100, 150, 200)  # player line, computer line, result line
