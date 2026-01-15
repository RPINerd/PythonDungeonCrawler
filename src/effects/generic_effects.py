"""
Generic effect implementations.

This module contains general-purpose effect classes that can be applied
to actors for various beneficial or detrimental effects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pdcglobal import D_ORDER, d

from .effect import Effect

if TYPE_CHECKING:
    from actor import Actor


class RegenerationEffect(Effect):

    """Regeneration effect that heals actor over time."""

    def __init__(self, host: Actor, owner: Actor | None = None) -> None:
        """
        Initialize regeneration effect with fixed duration.

        Args:
            host: The actor regenerating.
            owner: The actor applying the regeneration (optional).
        """
        dur = 10
        Effect.__init__(self, dur, host, owner)

    def tick(self) -> None:
        """Apply regeneration healing each tick."""
        a = -d(4)
        if self.host.cur_health - a > self.host.health:
            a = self.host.cur_health - self.host.health
        self.host.game.do_damage(self.host, a, D_ORDER)
        if self.host == self.host.game.player:
            self.host.game.shout("You are regenerating")
        else:
            self.host.game.shout("%s is regenerating" % (self.host.name))
        Effect.tick(self)
