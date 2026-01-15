"""
Chaos-based spell implementations.

This module contains spell classes that deal chaos damage, manipulate
creatures, and produce unpredictable magical effects.
"""

from __future__ import annotations

import random

from gfx.spell_fx import RayFX
from magic.magic import Spell
from pdcglobal import BLACK, D_CHAOS, GREEN, I_CORPSE, PURPLE, ST_GENERIC, d


class ChaosSpell(Spell):

    """Base class for chaos spells."""

    def __init__(self) -> None:
        """Initialize a chaos spell with purple color and generic type."""
        Spell.__init__(self)
        self.color = PURPLE
        self.type = ST_GENERIC


class FoulnessRay(ChaosSpell):

    """Single-target chaos ray that damages both caster and target."""

    def __init__(self) -> None:
        """Initialize Ray of Foulness with cost and description."""
        ChaosSpell.__init__(self)
        self.phys_cost = 5
        self.mind_cost = 5
        self.name = "Ray of Foulness"
        self.infotext = "Damage Foes with Chaos"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """
        Cast chaos ray at target position, dealing damage to caster and target.

        Args:
            pos: Target grid position (x, y) to aim the ray towards.
        """
        target = self.get_ray_target(self.caster.pos(), pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            fx = RayFX(BLACK, GREEN, self.caster.pos(), target.pos())
            self.game.drawGFX(fx)
            amount = d(self.caster.mind / 20) + self.caster.mind / 20
            self.game.do_damage(self.caster, amount / 2, D_CHAOS)
            self.game.do_damage(target, amount, D_CHAOS, self.caster)
            self.game.shout("%s befouled %s" % (self.caster.name, target.name))


class CorpseDance(ChaosSpell):

    """Corpse animation spell that raises undead creatures."""

    def __init__(self) -> None:
        """Initialize Corpse Dance with cost and description."""
        ChaosSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 45
        self.name = "Corpse Dance"
        self.infotext = "Reanimates corpse"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """
        Cast corpse dance at position, reanimating a corpse as undead ally.

        Args:
            pos: Target grid position (x, y) where a corpse is located.
        """
        targets = self.game.get_items_at(pos)
        random.shuffle(targets)
        for item in targets:
            if item.type == I_CORPSE:
                self.game.del_item(item)
                self.game.summon_monster(self.caster, "Skeleton", "easy_other", item.pos())
                return


class DrainLife(ChaosSpell):

    """Life drain spell that damages enemy and heals caster."""

    def __init__(self) -> None:
        """Initialize Drain Life with cost and description."""
        ChaosSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 45
        self.name = "Drain Life"
        self.infotext = "Damage Foes, heals self"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """
        Cast drain life ray at target, absorbing health.

        Args:
            pos: Target grid position (x, y) to drain life from.
        """
        target = self.get_ray_target(self.caster.pos(), pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            fx = RayFX(BLACK, GREEN, self.caster.pos(), target.pos())
            self.game.drawGFX(fx)
            amount = d(self.caster.mind / 20) + self.caster.mind / 20
            self.game.do_damage(self.caster, -amount / 2, D_CHAOS)
            self.game.do_damage(target, amount, D_CHAOS, self.caster)
            self.game.shout("%s drained %s" % (self.caster.name, target.name))
