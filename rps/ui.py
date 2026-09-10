"""Reusable drawing widgets: fonts, the gradient backdrop, buttons and the
lives meter.

Every class here draws onto a surface passed in by the caller and holds no
reference to the display, so each can be rendered to an offscreen surface in
a test.
"""

import math

import pygame

from . import config


def lerp_color(start, end, amount):
    """Blend two RGB colors, ``amount`` running 0.0 (start) to 1.0 (end)."""
    # "lerp" is the usual shorthand for linear interpolation: a straight blend between two values.
    # it is used here to drift the gradient's ends over time and shade the rows between them.
    return tuple(round(start[i] + (end[i] - start[i]) * amount) for i in range(3))


class Fonts:
    """The game's two type sizes.

    Built after ``pygame.font`` is initialised and passed to the widgets that
    need it, rather than created at import time as module-level globals.
    """

    def __init__(self):
        self.body = pygame.font.Font(None, config.BODY_FONT_SIZE)
        self.title = pygame.font.Font(None, config.TITLE_FONT_SIZE)


def draw_backed_text(surface, text, topleft, font,
                     color=config.TEXT_COLOR, backing=config.TEXT_BACKING):
    """Draw ``text`` on an opaque block so it stays legible over the gradient.

    Returns the rect that was drawn.
    """
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(topleft=topleft)
    pygame.draw.rect(surface, backing, rect)
    surface.blit(text_surface, rect)
    return rect


def draw_centered_text(surface, text, center, font, color, alpha=None):
    """Draw ``text`` centred on ``center``, optionally faded via ``alpha``."""
    text_surface = font.render(text, True, color)
    if alpha is not None:
        text_surface.set_alpha(alpha)
    surface.blit(text_surface, text_surface.get_rect(center=center))


class GradientBackground:
    """A vertical gradient whose two ends drift on a slow cosine cycle.

    The rendered surface is cached and only rebuilt when the rounded endpoint
    colors actually change, which at the default period is a few times a
    second rather than every frame.
    """

    def __init__(self, size=config.SCREEN_SIZE,
                 top=config.GRADIENT_TOP, bottom=config.GRADIENT_BOTTOM,
                 period_ms=config.GRADIENT_PERIOD_MS, bands=config.GRADIENT_BANDS):
        self._size = size
        self._top = top
        self._bottom = bottom
        self._period_ms = period_ms
        self._bands = bands
        self._cached_ends = None
        self._cached_surface = None

    def ends_at(self, ticks):
        """Return the (top, bottom) colors at ``ticks`` milliseconds.

        Uses cosine easing so the drift turns around smoothly at the end of a
        cycle instead of snapping back to the start.
        """
        phase = (1 - math.cos(2 * math.pi * ticks / self._period_ms)) / 2
        return (lerp_color(self._top[0], self._top[1], phase),
                lerp_color(self._bottom[0], self._bottom[1], phase))

    def _render(self, ends):
        """Build the full-size gradient surface for a pair of endpoint colors."""
        top, bottom = ends
        strip = pygame.Surface((1, self._bands))
        for y in range(self._bands):
            strip.set_at((0, y), lerp_color(top, bottom, y / (self._bands - 1)))
        return pygame.transform.smoothscale(strip, self._size)

    def draw(self, surface, ticks):
        """Fill ``surface`` with the gradient as it looks at ``ticks``."""
        ends = self.ends_at(ticks)
        if ends != self._cached_ends:
            self._cached_ends = ends
            self._cached_surface = self._render(ends)
        surface.blit(self._cached_surface, (0, 0))


class Button:
    """A clickable rectangle with a centred label.

    Replaces the per-button copies of the same draw-and-hit-test code. A
    button given a ``growth`` swells by that much while held down, keeping its
    top-left corner fixed; :attr:`rect` reflects the current size, so the
    grown button is also the one being hit-tested.
    """

    def __init__(self, rect, label, font, growth=(0, 0)):
        self.base_rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.growth = growth
        self.pressed = False

    @property
    def rect(self):
        """The button's current bounds, accounting for the press swell."""
        if not self.pressed:
            return self.base_rect.copy()
        grow_w, grow_h = self.growth
        return pygame.Rect(self.base_rect.left, self.base_rect.top,
                           self.base_rect.width + grow_w,
                           self.base_rect.height + grow_h)

    def contains(self, pos):
        """Return True if ``pos`` falls inside the button."""
        return self.rect.collidepoint(pos)

    def draw(self, surface, mouse_pos=None):
        """Draw the button, highlighting it if ``mouse_pos`` is over it."""
        rect = self.rect
        hovered = mouse_pos is not None and rect.collidepoint(mouse_pos)
        face = config.BUTTON_HOVER if hovered else config.BUTTON_FACE
        pygame.draw.rect(surface, face, rect)
        pygame.draw.rect(surface, config.BUTTON_BORDER, rect, config.BUTTON_BORDER_WIDTH)
        draw_centered_text(surface, self.label, rect.center, self.font, config.BUTTON_LABEL)


class LivesMeter:
    """The player's remaining lives, and the row of pips that shows them.

    Owns the count so the rules for spending and restoring live in one place;
    the count is clamped to ``maximum`` because only that many pips are drawn.
    """

    def __init__(self, font, maximum=config.STARTING_LIVES):
        self.font = font
        self.maximum = maximum
        self.remaining = maximum
        origin_x, origin_y = config.LIFE_PIP_ORIGIN
        size = config.LIFE_PIP_SIZE
        self._pips = [
            pygame.Rect(origin_x + i * config.LIFE_PIP_SPACING, origin_y, size, size)
            for i in range(maximum)
        ]

    @property
    def empty(self):
        """True once every life has been spent."""
        return self.remaining <= 0

    def reset(self):
        """Restore the meter to full, as at the start of a new game."""
        self.remaining = self.maximum

    def spend(self):
        """Take one life away and return True if that emptied the meter."""
        self.remaining = max(0, self.remaining - 1)
        return self.empty

    def restore(self):
        """Give one life back, never exceeding the starting count."""
        self.remaining = min(self.maximum, self.remaining + 1)

    def apply(self, outcome):
        """Apply a round's ``outcome`` to the meter.

        A loss spends a life, a win restores one, and a tie leaves the count
        alone. Returns True if this outcome emptied the meter.
        """
        if outcome.costs_a_life:
            return self.spend()
        if outcome.restores_a_life:
            self.restore()
        return False

    def draw(self, surface):
        """Draw the label and one pip per life, dimmed once spent."""
        draw_backed_text(surface, 'Lives', config.LIVES_LABEL_POS, self.font)
        for index, pip in enumerate(self._pips):
            spent = index >= self.remaining
            color = config.LIFE_SPENT_COLOR if spent else config.LIFE_PIP_COLOR
            pygame.draw.rect(surface, color, pip)
            pygame.draw.rect(surface, config.BUTTON_BORDER, pip, config.BUTTON_BORDER_WIDTH)
