"""Armor item suffix/modifier functions.

This module provides functions that apply suffixes and modifiers to
armor items, enhancing their properties.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from item.item import Item


def LesserProtection(item: Item) -> None:
    """Apply lesser protection bonus to armor item.

    Args:
        item: The armor item to modify.
    """
    item.full_name += " of lesser Protection"
    item.dv += random.randint(5, 25)
