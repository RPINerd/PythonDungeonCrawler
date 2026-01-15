"""
Book/scroll item suffix/modifier functions.

This module provides functions that apply suffixes and spell assignments
to book and scroll items.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from magic.chaos_spells import FoulnessRay
from magic.cold_spells import FrostRay
from magic.generic_spells import Identify, LesserHaste
from magic.order_spells import Healing, LesserHealing, Regeneration
from pdcglobal import IF_IDENTIFIED

if TYPE_CHECKING:
    from actor.actor import Actor
    from item.item import Item


def BookOfTOVU(item: Item) -> None:
    """
    Apply Book of TOVU suffix to book item.

    Args:
        item: The book item to modify.
    """
    pass


def BookOfRegeneration(item: Item) -> None:
    """
    Apply regeneration spell to book item.

    Args:
        item: The book item to modify.
    """
    item.full_name += " of Regeneration"
    item.spell = Regeneration


def BookOfIdentify(item: Item) -> None:
    """
    Apply identify spell to book item.

    Args:
        item: The book item to modify.
    """
    item.full_name += " of Identify"
    item.spell = Identify


def BookOfLesserHealing(item: Item) -> None:
    """
    Apply lesser healing spell to book item.

    Args:
        item: The book item to modify.
    """
    item.full_name += " of Lesser Healing"
    item.spell = LesserHealing


def BookOfHealing(item: Item) -> None:
    """
    Apply healing spell to book item.

    Args:
        item: The book item to modify.
    """
    item.full_name += " of Healing"
    item.spell = Healing


def BookOfFoulnessRay(item: Item) -> None:
    """
    Apply foulness ray spell to book item.

    Args:
        item: The book item to modify.
    """
    item.full_name += " of Foulness-Ray"
    item.spell = FoulnessRay


def BookOfFrostRay(item: Item) -> None:
    """
    Apply frost ray spell to book item.

    Args:
        item: The book item to modify.
    """
    item.full_name += " of Frost-Ray"
    item.spell = FrostRay


def BookOfLesserHaste(item: Item) -> None:
    """
    Apply lesser haste spell to book item.

    Args:
        item: The book item to modify.
    """
    item.full_name += " of Lesser Haste"
    item.spell = LesserHaste


def ReadBookOfTOVU(self: Item, actor: Actor) -> None:
    """
    Read the Book of Vile Umbrages.

    Args:
        self: The book item being read.
        actor: The actor reading the book.
    """
    actor.game.shout("Your read the Book of Vile Umbrages")


def ReadGenericBook(self, actor):
    learn_spell(self, actor)


def learn_spell(book, actor):
    if not book.flags & IF_IDENTIFIED:
        book.flags ^= IF_IDENTIFIED
    s = book.spell()
    actor.timer += actor.cur_speed * 3
    for spell in actor.spells:
        if isinstance(spell, book.spell):
            actor.game.shout("You already know the %s-Spell" % (s.name))
            return
    actor.spells.append(s)
    actor.game.shout("You learned the %s-Spell" % (s.name))
