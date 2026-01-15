"""Base magic spell class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pdcglobal import ST_GENERIC, WHITE, line

if TYPE_CHECKING:
    from actor.actor import Actor
    from engine import Engine


class Spell:

    """Base class for all spells."""

    game: Engine | None = None

    def __init__(self) -> None:
        """Initialize spell with default values."""
        self.phys_cost: int = 10
        self.mind_cost: int = 25
        self.name: str = "generic"
        self.infotext: str = "nothing"
        self.color: tuple[int, int, int] = WHITE
        self.type: int = ST_GENERIC

    def get_ray_target(self, cpos: tuple[int, int], tpos: tuple[int, int]) -> Actor | None:
        """
        Get target actor along a ray path.

        Args:
            cpos: Caster position
            tpos: Target position

        Returns:
            First actor hit by ray, or caster if same position, or None
        """
        if cpos != tpos:
            poss = line(cpos[0], cpos[1], tpos[0], tpos[1])
            poss.pop(0)
            for pos in poss:
                actor = self.game.get_actor_at(pos)
                if actor is not None:
                    return actor
        else:
            return self.caster
        return None

    def cast(self, caster: Actor) -> None:
        """
        Cast the spell.

        Args:
            caster: Actor casting the spell
        """
        self.caster = caster
        self.game.wait_for_target(self.target_choosen)

    def info(self) -> list[str]:
        """Get spell information for display."""
        lines = ["PHY: %i MND: %i" % (self.phys_cost, self.mind_cost)]
        if isinstance(self.infotext, str):
            lines.append(self.infotext)
        else:
            for i in self.infotext:
                lines.append(i)
        return lines
