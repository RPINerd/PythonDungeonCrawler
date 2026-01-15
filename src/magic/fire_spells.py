"""
Fire-based spell implementations.

This module contains spell classes that deal fire damage and apply
fire-related effects to targets and areas.
"""

from __future__ import annotations

from gfx.spell_fx import BallFX, RayFX
from magic.magic import Spell
from pdcglobal import D_FIRE, RED, ST_GENERIC, YELLOW, d


class FireSpell(Spell):

    """Base class for fire spells."""

    def __init__(self) -> None:
        """Initialize a fire spell with fire color and generic type."""
        Spell.__init__(self)
        self.color = RED
        self.type = ST_GENERIC


class FireBall(FireSpell):

    """Fireball spell that creates an explosion of fire in an area."""

    def __init__(self) -> None:
        """Initialize Fireball with cost and description."""
        FireSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 35
        self.name = "Fireball"
        self.infotext = "Causes a ball of Fire to explode"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """
        Cast fireball at target position, dealing fire damage in area.

        Args:
            pos: Target grid position (x, y) for the spell center.
        """
        radius = 1 + (self.caster.mind - 100) / 50
        fx = BallFX(RED, YELLOW, self.caster.pos(), pos, radius)
        self.game.drawGFX(fx)
        actors = self.caster.game.get_all_srd_actors(pos, radius, True)
        for act in actors:
            amount = d(self.caster.mind / 20) + self.caster.mind / 20 + 2
            self.game.do_damage(act, amount, D_FIRE, self.caster)
            self.game.shout("%s burns %s" % (self.caster.name, act.name))


class HeatRay(FireSpell):

    """Single-target heat ray spell that damages one enemy."""

    def __init__(self) -> None:
        """Initialize Heat Ray with cost and description."""
        FireSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 30
        self.name = "Heat Ray"
        self.infotext = "Damage Foes with Fire"

    def target_choosen(self, pos: tuple[int, int]) -> None:
        """
        Cast heat ray at target position, damaging the first enemy hit.

        Args:
            pos: Target grid position (x, y) to aim the ray towards.
        """
        target = self.get_ray_target(self.caster.pos(), pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            fx = RayFX(RED, YELLOW, self.caster.pos(), target.pos())
            self.game.drawGFX(fx)
            amount = d(self.caster.mind / 20) + self.caster.mind / 10 + 3
            self.game.do_damage(target, amount, D_FIRE, self.caster)
            self.game.shout("%s burns %s" % (self.caster.name, target.name))


#        target = self.get_ray_target(self.caster.pos(), pos)
#        if target is None:
#            self.game.shout('Your spell fizzles')
#        else:
#            fx = RayFX(WHITE,BLUE,self.caster.pos(),target.pos())
#            self.game.drawGFX(fx)
#            amount = d(self.caster.mind / 20) + self.caster.mind / 20
#            self.game.do_damage(target, amount, D_COLD,self.caster)
#            self.game.shout('%s freezed %s' % (self.caster.name, target.name))
