"""
Potion item suffix/modifier functions.

This module provides functions that apply suffixes and effects to
potion items, defining their drinking effects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from effects.av_effects import KillerbeePoisonEffect, YumuraPoisonEffect
from effects.generic_effects import RegenerationEffect
from pdcglobal import d

if TYPE_CHECKING:
    from actor.actor import Actor
    from item.item import Item


def PotionOfKillbeePoison(item: Item) -> None:
    """
    Apply killerbee poison suffix to potion.

    Args:
        item: The potion item to modify.
    """
    item.full_name += " of Killerbee-Poison"
    item.weaponinfotext = "Dangerous Poison"


def DrinkPotionOfKillbeePoison(self: Item, actor: Actor) -> None:
    """
    Apply killerbee poison effect when drinking potion.

    Args:
        self: The potion item being consumed.
        actor: The actor drinking the potion.
    """
    KillerbeePoisonEffect(actor, None)


def PotionOfYumuraPoison(item: Item) -> None:
    """
    Apply yumura poison suffix to potion.

    Args:
        item: The potion item to modify.
    """
    item.full_name += " of Yumura-Poison"


def DrinkPotionOfYumuraPoison(self: Item, actor: Actor) -> None:
    """
    Apply yumura poison effect when drinking potion.

    Args:
        self: The potion item being consumed.
        actor: The actor drinking the potion.
    """
    YumuraPoisonEffect(actor, None)


def PotionOfRegeneration(item: Item) -> None:
    """
    Apply regeneration suffix to potion.

    Args:
        item: The potion item to modify.
    """
    item.full_name += " of Killerbee-Poison"


def DrinkPotionOfRegeneration(self: Item, actor: Actor) -> None:
    """
    Apply regeneration effect when drinking potion.

    Args:
        self: The potion item being consumed.
        actor: The actor drinking the potion.
    """
    RegenerationEffect(actor, None)


def PotionOfEndurance(item: Item) -> None:
    """
    Apply endurance suffix to potion.

    Args:
        item: The potion item to modify.
    """
    item.full_name += " of Endurance"


def DrinkPotionOfEndurance(self: Item, actor: Actor) -> None:
    """
    Restore endurance when drinking potion.

    Args:
        self: The potion item being consumed.
        actor: The actor drinking the potion.
    """
    actor.cur_endurance += d(10) + d(10)


def PotionOfMind(item: Item) -> None:
    """
    Apply mind suffix to potion.

    Args:
        item: The potion item to modify.
    """
    item.full_name += " of Mind"


def DrinkPotionOfMind(self: Item, actor: Actor) -> None:
    """
    Restore mind when drinking potion.

    Args:
        self: The potion item being consumed.
        actor: The actor drinking the potion.
    """
    actor.cur_mind += d(10) + d(10)


def PotionOfSpellcaster(item: Item) -> None:
    """
    Apply spellcaster suffix to potion.

    Args:
        item: The potion item to modify.
    """
    item.full_name += " of Spellcasters"


def DrinkPotionOfSpellcaster(self: Item, actor: Actor) -> None:
    """
    Restore endurance and mind when drinking potion.

    Args:
        self: The potion item being consumed.
        actor: The actor drinking the potion.
    """
    actor.cur_endurance += d(10) + d(10)
    actor.cur_mind += d(10) + d(10)


def PotionOfHealing(item: Item) -> None:
    """
    Apply healing suffix to potion.

    Args:
        item: The potion item to modify.
    """
    item.full_name += " of Healing"


def DrinkPotionOfHealing(self: Item, actor: Actor) -> None:
    """
    Restore health when drinking potion.

    Args:
        self: The potion item being consumed.
        actor: The actor drinking the potion.
    """
    actor.cur_health += d(10)
