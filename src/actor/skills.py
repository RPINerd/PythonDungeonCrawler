from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from actor.actor import Actor


class Skills:
    """Manages character combat and ability skills."""

    def __init__(self, host: Actor) -> None:

        skills = {
            "Flail": host.STR + host.DEX,
            "Flail2H": host.STR + host.DEX,
            "Sword": host.STR + host.DEX,
            "Sword2H": host.STR + host.DEX,
            "Axe": host.STR + host.DEX,
            "Axe2H": host.STR + host.DEX,
            "Polearm": host.STR + host.DEX,
            "Polearm2H": host.STR + host.DEX,
            "Hammer": host.STR + host.DEX,
            "Hammer2H": host.STR + host.DEX,
            "Rapier": host.STR + host.DEX,
            "Dagger": host.STR + host.DEX,
            "Spear": host.STR + host.DEX,
            "Bow": host.DEX,
            "Crossbow": host.DEX,
            "Sling": host.DEX,
            "Throwing": host.DEX,
            "Dodge": host.DEX + 10 - host.SIZ,
            "Resilence": host.CON + host.POW,
            "Unarmed": host.STR + host.DEX,
        }

        for skill in skills:
            self.__dict__[skill] = skills[skill]

        self.__dict__["skills"] = skills
        self.__dict__["host"] = host

    def __getstate__(self) -> dict[str, Any]:
        """Return state for pickling."""
        return self.__dict__

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Restore state from pickling."""
        for item in state:
            self.__dict__[item] = state[item]

    def __getattr__(self, attr: str) -> Any:
        """Get attribute dynamically."""
        return self.__dict__[attr]

    def __setattr__(self, attr: str, value: Any) -> None:
        """Set attribute dynamically."""
        self.__dict__[attr] = value
