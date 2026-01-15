"""
Order-based spell implementations.

This module contains spell classes that heal, protect, and apply
beneficial effects to allies and the caster.
"""

from __future__ import annotations

from effects import generic_effects
from pdcglobal import ST_ORDER, WHITE, d

from .magic import Spell


class OrderSpell(Spell):

    """Base class for order spells."""

    def __init__(self) -> None:
        """Initialize an order spell with white color and order type."""
        Spell.__init__(self)
        self.color = WHITE
        self.type = ST_ORDER


class Regeneration(OrderSpell):

    """Regeneration spell that heals target over time."""

    def __init__(self) -> None:
        """Initialize Regeneration with cost and description."""
        OrderSpell.__init__(self)
        self.phys_cost = 25
        self.mind_cost = 65
        self.name = "Regeneraton"
        self.infotext = "Target regenerates"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """
        Apply regeneration effect to target actor at position.

        Args:
            pos: Target grid position (x, y) to apply regeneration to.
        """
        target = self.game.get_actor_at(pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            self.game.shout("%s regenerate %s" % (self.caster.name, target.name))
            r = generic_effects.RegenerationEffect(target, self.caster)
            r.tick()


class LesserHealing(OrderSpell):

    """Lesser healing spell that restores small amounts of health."""

    def __init__(self) -> None:
        """Initialize Lesser Healing with cost and description."""
        OrderSpell.__init__(self)
        self.phys_cost = 5
        self.mind_cost = 25
        self.name = "Lesser Healing"
        self.infotext = "Cures small wounds"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """
        Heal target actor at position, restoring minor health.

        Args:
            pos: Target grid position (x, y) to heal.
        """
        target = self.game.get_actor_at(pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            amount = d(self.caster.mind / 10) + 3
            if target.cur_health + amount > target.health:
                amount = target.health - target.cur_health
            self.game.do_damage(target, -amount)
            self.game.shout("%s healed %s" % (self.caster.name, target.name))


class Healing(OrderSpell):

    """Healing spell that restores moderate amounts of health."""

    def __init__(self) -> None:
        """Initialize Healing with cost and description."""
        OrderSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 55
        self.name = "Healing"
        self.infotext = "Cures wounds"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """
        Heal target actor at position, restoring significant health.

        Args:
            pos: Target grid position (x, y) to heal.
        """
        target = self.game.get_actor_at(pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            amount = d(self.caster.mind / 10) + d(self.caster.mind / 10) + 5
            self.game.do_damage(target, -amount)
            self.game.shout("%s healed %s" % (self.caster.name, target.name))
