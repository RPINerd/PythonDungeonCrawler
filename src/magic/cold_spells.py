"""
Cold-based spell implementations.

This module contains spell classes that deal cold damage and freeze
enemies with ice-based effects.
"""

from __future__ import annotations

from gfx.spell_fx import RayFX
from magic.magic import Spell
from pdcglobal import BLUE, D_COLD, ST_GENERIC, WHITE, d


class ColdSpell(Spell):

    """Base class for cold spells."""

    def __init__(self) -> None:
        """Initialize a cold spell with blue color and generic type."""
        Spell.__init__(self)
        self.color = BLUE
        self.type = ST_GENERIC


class FrostRay(ColdSpell):

    """Single-target frost ray spell that deals cold damage."""

    def __init__(self) -> None:
        """Initialize Frost Ray with cost and description."""
        ColdSpell.__init__(self)
        self.phys_cost = 5
        self.mind_cost = 30
        self.name = "Frost Ray"
        self.infotext = "Damage Foes with cold"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """
        Cast frost ray at target position, damaging the first enemy hit.

        Args:
            pos: Target grid position (x, y) to aim the ray towards.
        """
        target = self.get_ray_target(self.caster.pos(), pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            fx = RayFX(WHITE, BLUE, self.caster.pos(), target.pos())
            self.game.drawGFX(fx)
            amount = d(self.caster.mind / 20) + self.caster.mind / 10 + 2
            self.game.do_damage(target, amount, D_COLD, self.caster)
            self.game.shout("%s freezed %s" % (self.caster.name, target.name))
