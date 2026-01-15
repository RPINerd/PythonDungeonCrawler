from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine


class Att:

    """Attribute that can be improved with experience points."""

    game: Engine | None = None

    def __init__(self, name: str, info: str, cost: int = 30) -> None:
        self.cost: int = cost
        self.name: str = name
        self.__info__: str = info

    def info(self) -> list[str]:
        """Get information about the attribute's current value and improvement cost."""
        return ["Current: %i" % (getattr(self.game.player, self.name.lower())), "Cost: %i XP" % (self.cost)]
