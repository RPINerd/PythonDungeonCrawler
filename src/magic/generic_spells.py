"""Generic spell implementations.

This module contains spell classes that provide utility effects like
haste and identification.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from magic.magic import Spell
from pdcglobal import GREEN, ST_GENERIC, d

if TYPE_CHECKING:
    from actor import Actor


class GenericSpell(Spell):
    """Base class for generic utility spells."""

    def __init__(self) -> None:
        """Initialize a generic spell with green color and generic type."""
        Spell.__init__(self)
        self.color = GREEN
        self.type = ST_GENERIC


class LesserHaste(GenericSpell):
    """Lesser haste spell that increases target's movement speed."""

    def __init__(self) -> None:
        """Initialize Lesser Haste with cost and description."""
        GenericSpell.__init__(self)
        self.phys_cost = 5
        self.mind_cost = 15
        self.name = "Lesser Haste"
        self.infotext = "Speed Up"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """Apply haste effect to target actor, increasing movement speed.

        Args:
            pos: Target grid position (x, y) to hasten.
        """
        target = self.game.get_actor_at(pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            amount = d(self.caster.mind / 10) + 3
            if target.cur_speed > target.speed / 2:
                target.cur_speed -= amount
            self.game.shout("%s speeds up %s" % (self.caster.name, target.name))


class Identify(GenericSpell):
    """Identification spell that reveals item properties."""

    def __init__(self) -> None:
        """Initialize Identify with cost and description."""
        GenericSpell.__init__(self)
        self.phys_cost = 0
        self.mind_cost = 25
        self.name = "Identify"
        self.infotext = "Identify an Item"

    def cast(self, caster: Actor) -> None:
        """Begin identification spell cast.

        Args:
            caster: The actor casting the spell.
        """
        self.caster = caster
        self.game.do_identify()
