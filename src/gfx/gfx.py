"""Graphics base class for game visual elements."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

if TYPE_CHECKING:
    from engine import Engine


class GFX:
    """Base class for graphics elements (projectiles, effects, etc)."""

    game: Engine | None = None

    def __init__(self) -> None:
        """Initialize graphics element."""
        self.redraw: bool = True
        self.xoff: int = 0
        self.yoff: int = 0

    def get_surf(self) -> pygame.Surface | None:
        """Get the surface to render. Override in subclasses."""
        pass

    def pos(self) -> tuple[int, int] | None:
        """Get current position. Override in subclasses."""
        pass

    def tick(self) -> None:
        """Process one game tick. Override in subclasses."""
        pass
