"""Projectile graphics for ranged attacks."""

from __future__ import annotations

from collections.abc import Generator

import pygame

from pdcglobal import (
    MOVE_DOWN,
    MOVE_DOWN_LEFT,
    MOVE_DOWN_RIGHT,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    MOVE_UP_LEFT,
    MOVE_UP_RIGHT,
    TILESIZE,
    line,
)
from pdcresource import Res

from .gfx import GFX


class ProjectileFX(GFX):

    """Graphics for projectiles in flight."""

    rescache: Res | None = None

    def __init__(self, dir: int, s_pos: tuple[int, int], t_pos: tuple[int, int], type: str = "Arrow") -> None:
        GFX.__init__(self)

        if ProjectileFX.rescache is None:
            ProjectileFX.rescache = Res("dc-item.png", TILESIZE)

        if type == "Arrow":
            img = 73
        if dir == MOVE_UP:
            img = img
        if dir == MOVE_UP_RIGHT:
            img += 1
        if dir == MOVE_RIGHT:
            img += 2
        if dir == MOVE_DOWN_RIGHT:
            img += 3
        if dir == MOVE_DOWN:
            img += 4
        if dir == MOVE_DOWN_LEFT:
            img += 5
        if dir == MOVE_LEFT:
            img += 6
        if dir == MOVE_UP_LEFT:
            img += 7

        self.image: pygame.Surface = self.rescache.get(img)

        self.__pos_gen: Generator[tuple[int, int]] = self.__pos(s_pos, t_pos)
        self.redraw: bool = True

    def __pos(self, s_pos: tuple[int, int], t_pos: tuple[int, int]) -> Generator[tuple[int, int]]:
        """Generator yielding positions along projectile path."""
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
        """Get the projectile surface."""
        return self.image

    def pos(self) -> tuple[int, int] | None:
        try:
            pos = self.__pos_gen.next()
            return pos
        except StopIteration or AttributeError:
            return None
        except Exception as e:
            print(f"Unexpected Exception {e} in ProjectileFX.pos()")
            return None

    def tick(self):
        pass
