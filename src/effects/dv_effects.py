"""
Damage/visual effect implementations.

This module contains effect classes that deal visual and damage effects,
including stun, acid, frost, heat, and splitting effects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import dungeon
from pdcglobal import D_ACID, D_COLD, D_FIRE, d

from .effect import Effect

if TYPE_CHECKING:
    from actor import Actor


class FloatingEyeGazeEffect(Effect):

    """Stun effect from Floating Eye gaze."""

    def __init__(self, host: Actor, owner: Actor | None = None) -> None:
        """
        Initialize stun effect with random duration.

        Args:
            host: The actor being stunned.
            owner: The actor causing the stun effect (optional).
        """
        dur = d(10)
        Effect.__init__(self, dur, host, owner)

    def tick(self) -> None:
        """Apply stun effect each tick, adding to timer."""
        self.host.timer += 1000
        if self.host == self.host.game.player:
            self.host.game.shout("You are stunned by the Floating Eye`s gaze!")
        else:
            self.host.game.shout("%s is stunned by the Floating Eye`s gaze!" % (self.host.name))

        Effect.tick(self)


class AcidSplatterEffect(Effect):

    """Acid splash effect that applies to multiple actors."""

    notrigger: list = []

    def __init__(self, host: Actor, owner: Actor) -> None:
        """
        Initialize acid splatter effect on all nearby actors.

        Args:
            host: The primary actor being splashed.
            owner: The actor causing the acid effect.
        """
        dur = 1
        Effect.__init__(self, dur, host, owner)
        actors = owner.game.get_all_srd_actors(owner.pos())
        for act in actors:
            Effect.__init__(self, dur, act, owner)

    def tick(self) -> None:
        """Apply acid damage each tick."""
        self.host.game.do_damage(self.host, d(3), D_ACID, self.owner)
        if self.host == self.host.game.player:
            self.host.game.shout("You are splashed by acid!")
        else:
            self.host.game.shout("%s is splashed by acid!" % (self.host.name))
        Effect.tick(self)


class FrostEffect(Effect):

    """Frost/freeze effect that deals cold damage."""

    def __init__(self, host: Actor, owner: Actor | None = None) -> None:
        """
        Initialize frost effect with short duration.

        Args:
            host: The actor being frozen.
            owner: The actor causing the frost effect (optional).
        """
        dur = 1
        Effect.__init__(self, dur, host, owner)

    def tick(self) -> None:
        """Apply cold damage each tick."""
        self.host.game.do_damage(self.host, d(3), D_COLD, self.owner)
        if self.host == self.host.game.player:
            self.host.game.shout("You are freezing!")
        else:
            self.host.game.shout("%s is freezing!" % (self.host.name))
        Effect.tick(self)


class HeatEffect(Effect):

    """Heat/burn effect that deals fire damage."""

    def __init__(self, host: Actor, owner: Actor | None = None) -> None:
        """
        Initialize heat effect with short duration.

        Args:
            host: The actor being burned.
            owner: The actor causing the heat effect (optional).
        """
        dur = 1
        Effect.__init__(self, dur, host, owner)

    def tick(self) -> None:
        """Apply fire damage each tick."""
        self.host.game.do_damage(self.host, d(3), D_FIRE, self.owner)
        if self.host == self.host.game.player:
            self.host.game.shout("You are getting burned!")
        else:
            self.host.game.shout("%s is getting burned!" % (self.host.name))
        Effect.tick(self)


class SplitEffect(Effect):

    """Split effect that replicates creatures."""

    notrigger: list = []

    def __init__(self, host: Actor, owner: Actor) -> None:
        """
        Initialize split effect for creature replication.

        Args:
            host: The creature being split.
            owner: The creature causing the split effect.
        """
        dur = 1
        Effect.__init__(self, dur, host, owner)

    def tick(self) -> None:
        """Apply split effect, potentially creating new creature."""
        new_pos = self.host.game.get_free_adj(self.owner.pos())
        if new_pos is not None:
            self.owner.game.shout("%s splits in half!" % (self.owner.name))
            new = dungeon.Populator.create_creature(self.owner.pop_name, self.owner.filename)
            new.set_pos(new_pos)
            new.game.add_actor(new)
            self.owner.health = self.owner.health / 2 + 1
            self.owner.cur_health = self.owner.cur_health / 2 + 1
            new.health = self.owner.health
            new.cur_health = self.owner.cur_health
            new.xp_value = self.owner.xp_value / 3 + 2
        Effect.tick(self)


class DazzleEffect(Effect):

    """Dazzle effect that temporarily confuses vision."""

    def __init__(self, host: Actor, owner: Actor | None = None) -> None:
        """
        Initialize dazzle effect with random duration.

        Args:
            host: The actor being dazzled.
            owner: The actor causing the dazzle effect (optional).
        """
        dur = d(4)
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Blinds the enemy"

    def tick(self):
        self.host.dazzled = True
        if self.host == self.host.game.player:
            self.host.game.shout("You are blinded!")
        else:
            self.host.game.shout("%s is blinded!" % (self.host.name))
        Effect.tick(self)
