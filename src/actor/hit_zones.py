from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pdcglobal import L_ABDOMEN, L_ARMS, L_CHEST, L_HEAD, L_LEGS, d

if TYPE_CHECKING:
    from actor.actor import Actor


def leg(tot: int) -> int:
    """Calculate hit points for leg zone."""
    tot += 4
    return tot // 5


def head(tot: int) -> int:
    """Calculate hit points for head zone."""
    tot += 4
    return tot // 5


def arm(tot: int) -> int:
    """Calculate hit points for arm zone."""
    tot += 4
    v = tot // 5 - 1
    return max(v, 1)


def chest(tot: int) -> int:
    """Calculate hit points for chest zone."""
    tot += 4
    return tot // 5 + 2


def abdomen(tot: int) -> int:
    """Calculate hit points for abdomen zone."""
    tot += 4
    return tot // 5 + 1


class HitZones:
    """Manages locational hit points for an actor."""

    def __init__(self, host: Actor) -> None:

        tot = host.SIZ + host.CON

        # cur/max
        zones = {
            "L_Leg": (leg(tot), leg(tot), "left leg", L_LEGS),
            "R_Leg": (leg(tot), leg(tot), "right leg", L_LEGS),
            "L_Arm": (arm(tot), arm(tot), "left arm", L_ARMS),
            "R_Arm": (arm(tot), arm(tot), "right arm", L_ARMS),
            "Abdomen": (abdomen(tot), abdomen(tot), "abdomen", L_ABDOMEN),
            "Chest": (chest(tot), chest(tot), "chest", L_CHEST),
            "Head": (head(tot), head(tot), "head", L_HEAD),
        }

        for zone in zones:
            self.__dict__[zone] = zones[zone]

        self.__dict__["zones"] = zones
        self.__dict__["host"] = host

    def get_random_zone(self) -> str:
        """Get a random hit zone based on d20 roll."""
        z = d(20)
        if z <= 3:
            return "R_Leg"
        if z <= 6:
            return "L_Leg"
        if z <= 9:
            return "Abdomen"
        if z <= 12:
            return "Chest"
        if z <= 15:
            return "R_Arm"
        if z <= 18:
            return "L_Arm"
        return "Head"

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
