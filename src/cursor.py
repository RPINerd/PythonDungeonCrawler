from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from pdcglobal import TILESIZE, get_new_pos
from pdcresource import Res

if TYPE_CHECKING:
    from engine import Engine


class Cursor:

    """Cursor for selecting positions in the game world."""

    def __init__(self, game: Engine) -> None:
        self.game: Engine = game
        self.x: int = 0
        self.y: int = 0
        self.cursor_surf: pygame.Surface | None = None

    def get_surf(self) -> pygame.Surface:
        """Get the cursor surface, loading it if necessary."""
        if self.cursor_surf is None:
            res = Res("cursor.png", TILESIZE)
            self.cursor_surf = res.get(0)
        return self.cursor_surf

    def pos(self) -> tuple[int, int]:
        """Get current cursor position."""
        return self.x, self.y

    def set_pos(self, pos: tuple[int, int]) -> None:
        """Set cursor position."""
        self.x = pos[0]
        self.y = pos[1]

    def move(self, direction: int) -> None:
        """Move cursor in specified direction and display info about destination."""
        new_pos = get_new_pos(self.pos(), direction)
        if not (self.game.player.sc.lit(new_pos[0], new_pos[1]) or new_pos == self.game.player.pos()):
            return
        actor = self.game.get_actor_at(new_pos)
        if actor is not None:
            self.game.shout("You see a %s" % (actor.name))
        items = self.game.get_items_at(new_pos)
        if len(items) == 1:
            self.game.shout("You see a %s" % (items[0].get_name()))
        if len(items) > 1:
            self.game.shout("You see several items here")
        self.set_pos(new_pos)
