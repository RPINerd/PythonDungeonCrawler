"""Set up the various RPG class choices for the player"""

from __future__ import annotations

from typing import TYPE_CHECKING

import magic
from dungeon.populator import Populator

if TYPE_CHECKING:
    from actor.actor import Actor


class Class:

    """Base class for character classes."""

    def __init__(self, host: Actor) -> None:
        self.host: Actor = host


class Fighter(Class):

    """Fighter class skilled with all weapons."""

    desc = "Thanks to unremittingly training, $$$ was skilled at all weapons."

    def __init__(self, host: Actor) -> None:
        Class.__init__(self, host)
        i = Populator.create_item("Flail", "basic_weapons", 2)
        self.host.pick_up(i)
        self.host.equip(i)

        c = Populator.create_item("ChainmailShirt", "basic_armor", 2)
        self.host.pick_up(c)
        self.host.equip(c)

        b = Populator.create_item("Bow", "basic_weapons", 0)
        self.host.pick_up(b)

        for _ in range(0, 3):
            r = Populator.create_item("Arrows", "basic_weapons", 0)
            self.host.pick_up(r)

        for _ in range(0, 3):
            r = Populator.create_item("Darts", "basic_weapons", 0)
            self.host.pick_up(r)

        # if hasattr(self.host.slot,'trousers'):
        #    t = Populator.create_item('Trousers', 'basic_stuff', 2)
        #    self.host.pick_up(t)
        #    self.host.equip(t)
        self.host.timer = 0


class Barbarian(Class):

    """Barbarian class specializing in axes."""

    desc = "Since his youth, $$$ clearly loved one weapon the most: the Axe."

    def __init__(self, host: Actor) -> None:
        Class.__init__(self, host)
        i = Populator.create_item("Axe", "basic_weapons", 25)
        self.host.pick_up(i)
        self.host.equip(i)

        if hasattr(self.host.slot, "trousers"):
            t = Populator.create_item("Trousers", "basic_stuff", 2)
            self.host.pick_up(t)
            self.host.equip(t)
        self.host.timer = 0


class Priest(Class):

    """Priest class devoted to law and order."""

    desc = "Since %%% birth, $$$ stood up for Law and Order."

    def __init__(self, host: Actor) -> None:
        Class.__init__(self, host)
        self.host.timer = 0


class Sorcerer(Class):

    """Sorcerer class mastering elemental forces."""

    desc = "All %%% live $$$ tried to master the Elemental-Forces "

    def __init__(self, host: Actor) -> None:
        Class.__init__(self, host)
        self.host.spells.append(magic.fire_spells.FireBall())
        self.host.timer = 0


class Necromancer(Class):

    """Necromancer class wielding chaos magic."""

    desc = "Allured by the Power of Chaos, $$$ was a fearsome Wizrad."

    def __init__(self, host: Actor) -> None:
        Class.__init__(self, host)
        self.host.spells.append(magic.chaos_spells.CorpseDance())
        self.host.spells.append(magic.chaos_spells.DrainLife())
        self.host.timer = 0


classkits = (
    ("Fighter", Fighter),
    ("Barbarian", Barbarian),
    ("Sorcerer", Sorcerer),
    ("Priest", Priest),
    ("Necromancer", Necromancer),
)
