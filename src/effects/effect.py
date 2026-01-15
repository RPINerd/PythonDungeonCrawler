"""Base effect class for temporary status effects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pdcglobal import IF_RANGED

if TYPE_CHECKING:
    from actor.actor import Actor


class Effect:

    """Base class for temporary status effects on actors."""

    notrigger: list[int] = [IF_RANGED]

    def __init__(self, duration: int, host: Actor, owner: Actor | None) -> None:
        """
        Initialize an effect.

        Args:
            duration: Number of turns effect lasts
            host: Actor being affected
            owner: Actor who caused the effect (optional)
        """
        self.duration: int = duration
        self.host: Actor = host
        self.owner: Actor | None = owner
        host.running_fx.append(self)

    def tick(self) -> None:
        """Process one turn of the effect."""
        self.duration -= 1
        if self.duration <= 0:
            if self in self.host.running_fx:
                self.host.running_fx.remove(self)
