from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine


class Camera:

    """Camera for managing viewport in the game world."""

    game: Engine | None = None

    def __init__(self, h: int, w: int) -> None:
        self.height: int = h
        self.width: int = w
        self.x: int = 0
        self.y: int = 0
        self.edge: int = 7

    def get_view_port(self) -> tuple[int, int, int, int]:
        """Get the current viewport bounds."""
        return self.x, self.y, self.x + self.width, self.y + self.height

    def is_in_view(self, x: int, y: int) -> bool:
        if x >= self.x and x <= self.x + self.width:
            if y >= self.y and y <= self.y + self.height:
                return True
        return False

    def adjust(self, pos: tuple[int, int]) -> bool:
        """Adjust camera position to keep position in view. Returns True if adjusted."""
        x, y = pos
        adj = False
        # adjust to down
        if y - self.y > self.height - self.edge:
            self.y += 1
            adj = True
        # adjust to up
        if y - self.y < self.edge:
            self.y -= 1
            adj = True

        # adjust to right
        if x - self.x > self.width - self.edge:
            self.x += 1
            adj = True
        # adjust to up
        if x - self.x < self.edge:
            self.x -= 1
            adj = True
        return adj
