"""Throw graphics for thrown items."""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

import pygame

from pdcglobal import TILESIZE, line

from .gfx import GFX

if TYPE_CHECKING:
    from item.item import Item

# from pdcresource import Res


class ThrowFX(GFX):

    """Graphics for thrown items in flight."""

    rescache: object | None = None

    def __init__(self, dir: int, s_pos: tuple[int, int], t_pos: tuple[int, int], item: Item) -> None:
        """
        Initialize thrown item graphics.

        Args:
            dir: Direction of throw
            s_pos: Starting position
            t_pos: Target position
            item: Item being thrown
        """
        GFX.__init__(self)

        self.image: pygame.Surface = item.get_dd_img()

        self.__pos_gen: Generator[tuple[int, int]] = self.__pos(s_pos, t_pos)
        self.redraw: bool = True

    def __pos(self, s_pos: tuple[int, int], t_pos: tuple[int, int]) -> Generator[tuple[int, int]]:
        """Generator yielding positions along throw path."""
        s_real = (
            s_pos[0] * TILESIZE - self.game.camera.x * TILESIZE,
            s_pos[1] * TILESIZE - self.game.camera.y * TILESIZE,
        )
        t_real = (
            t_pos[0] * TILESIZE - self.game.camera.x * TILESIZE,
            t_pos[1] * TILESIZE - self.game.camera.y * TILESIZE,
        )
        all = line(s_real[0], s_real[1], t_real[0], t_real[1])[::6]
        for pos in all:
            yield pos

    def get_surf(self) -> pygame.Surface:
        """Get the thrown item surface."""
        return self.image

    def pos(self) -> tuple[int, int] | None:
        try:
            pos = self.__pos_gen.next()
            return pos
        except StopIteration or AttributeError:
            return None
        except Exception as e:
            print(f"Unexpected Exception {e} in ThrowFX.pos()")
            return None

    def tick(self):
        pass
