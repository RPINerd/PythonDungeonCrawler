"""
Item type class definitions.

This module contains specialized item subclasses for different equipment
categories like weapons, armor, shields, boots, helmets, etc.
"""

from __future__ import annotations

from item.item import Item
from pdcglobal import (
    I_AMMO,
    I_ARMOR,
    I_BOOTS,
    I_GOLD,
    I_HELMET,
    I_SHIELD,
    I_STUFF,
    I_TROUSERS,
    I_WEAPON,
    WT_UNARMED,
    cd,
)


class Armor(Item):

    """Armor item worn on body for protection."""

    def __init__(self, add: dict) -> None:
        """
        Initialize armor item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_ARMOR


class Cloak(Item):

    """Cloak item worn for protection and stealth."""

    def __init__(self, add: dict) -> None:
        """
        Initialize cloak item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_ARMOR


class Weapon(Item):

    """Weapon item for combat."""

    def __init__(self, add: dict) -> None:
        """
        Initialize weapon item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_WEAPON


class Unarmed(Item):

    """Unarmed combat item representing bare hands."""

    def __init__(self, add: dict) -> None:
        """
        Initialize unarmed weapon.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_WEAPON
        self.skills.append(WT_UNARMED)
        self.damage = "1D3", lambda: cd(1, 3)


class Shield(Item):

    """Shield item for blocking and defense."""

    def __init__(self, add: dict) -> None:
        """
        Initialize shield item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_SHIELD


class Boots(Item):

    """Boots item worn on feet."""

    def __init__(self, add: dict) -> None:
        """
        Initialize boots item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_BOOTS


class Helmet(Item):

    """Helmet item worn on head for protection."""

    def __init__(self, add: dict) -> None:
        """
        Initialize helmet item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_HELMET


class Trousers(Item):

    """Trousers item worn on legs."""

    def __init__(self, add: dict) -> None:
        """
        Initialize trousers item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_TROUSERS


class Ammo(Item):

    """Ammunition item for ranged weapons."""

    def __init__(self, add: dict) -> None:
        """
        Initialize ammunition item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_AMMO


class Gold(Item):

    """Gold currency item."""

    def __init__(self, add: dict) -> None:
        """
        Initialize gold item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_GOLD


class Stuff(Item):

    """Generic stuff item for miscellaneous objects."""

    def __init__(self, add: dict) -> None:
        """
        Initialize generic stuff item.

        Args:
            add: Dictionary of item properties.
        """
        Item.__init__(self, add)
        self.type = I_STUFF
