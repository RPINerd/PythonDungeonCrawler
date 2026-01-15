"""
Spell effect graphics implementations.

This module contains visual effect classes for spells, including
ball and ray effects with animation and rendering.
"""

from __future__ import annotations

import random
from collections.abc import Generator

import pygame

from gfx.gfx import GFX
from pdcglobal import TILESIZE, d, line


class BallFX(GFX):

    """Ball spell effect with explosion animation."""

    def __init__(
        self,
        color1: tuple[int, int, int],
        color2: tuple[int, int, int],
        s_pos: tuple[int, int],
        t_pos: tuple[int, int],
        radius: int = 1,
    ) -> None:
        """
        Initialize ball effect with colors and positions.

        Args:
            color1: Primary RGB color tuple.
            color2: Secondary RGB color tuple for animation.
            s_pos: Starting position (grid coordinates).
            t_pos: Target position (grid coordinates).
            radius: Explosion radius in tiles.
        """
        GFX.__init__(self)
        self.f_image: list[pygame.Surface] = []
        surf = pygame.Surface((32, 32), pygame.SRCALPHA, 32)
        pygame.draw.circle(surf, color1, (16, 16), 2, 2)
        self.f_image.append(surf)
        surf = pygame.Surface((32, 32), pygame.SRCALPHA, 32)
        pygame.draw.circle(surf, color2, (16, 16), 2, 2)
        self.f_image.append(surf)
        surf = pygame.Surface((32, 32), pygame.SRCALPHA, 32)
        pygame.draw.circle(surf, color1, (16, 16), 2, 2)
        self.f_image.append(surf)
        self.color1 = color1
        self.color2 = color2
        self.c = 0
        self.image = self.f_image[self.c]
        self.__pos_gen = self.__pos(s_pos, t_pos)
        self.redraw = False
        self.radius = radius
        self.cur_radius = 0
        self.explode = False
        self.finish = False
        self.lastpos: tuple[int, int] | None = None

    def __pos(
        self, s_pos: tuple[int, int], t_pos: tuple[int, int]
    ) -> Generator[tuple[int, int]]:
        """
        Generate positions along a line from start to target.

        Args:
            s_pos: Starting grid position.
            t_pos: Target grid position.

        Yields:
            Pixel coordinates along the path.
        """
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
        """
        Get current surface image for rendering.

        Returns:
            Current pygame Surface for the effect.
        """
        return self.image

    def pos(self) -> tuple[int, int] | None:
        """
        Get current position of the effect.

        Returns:
            Current (x, y) pixel coordinates or None if effect finished.
        """
        if not self.explode:
            try:
                pos = self.__pos_gen.next()
                self.lastpos = pos
                return pos
            except StopIteration or AttributeError:
                self.explode = True
                # self.redraw = True
                return self.lastpos
            except Exception as e:
                print(f"Unknown Exception {e} in BallFX.pos()")
                return None
        elif not self.finish:
            return self.lastpos[0] + self.xoff, self.lastpos[1] + self.yoff
        else:
            return None

    def tick(self) -> None:
        """Update animation frame and explosion state."""
        # self.c += 1
        # if self.c >= len(RayFX.f_image):
        #    self.c = 0
        if not self.explode:
            self.c = random.randint(0, len(self.f_image) - 1)
            self.image = self.f_image[self.c]
        else:
            # size = self.cur_radius
            max_size = int((self.radius + 0.5) * TILESIZE)

            self.image = pygame.Surface((max_size * 2, max_size * 2), pygame.SRCALPHA, 32)
            if d(100) > 20:
                color = self.color1
            else:
                color = self.color2

            width = 4
            width = min(width, int(self.cur_radius))
            pygame.draw.circle(self.image, color, (max_size, max_size), int(self.cur_radius), width)

            self.cur_radius += 4

            # size = (float(self.cur_radius) + 0.5) * TILESIZE
            self.xoff = -TILESIZE * self.radius
            self.yoff = -TILESIZE * self.radius
            if self.cur_radius >= max_size:
                self.finish = True


class RayFX(GFX):

    """Ray spell effect with animated projectile."""

    def __init__(
        self,
        color1: tuple[int, int, int],
        color2: tuple[int, int, int],
        s_pos: tuple[int, int],
        t_pos: tuple[int, int],
    ) -> None:
        """
        Initialize ray effect with colors and positions.

        Args:
            color1: Primary RGB color tuple.
            color2: Secondary RGB color tuple for animation.
            s_pos: Starting position (grid coordinates).
            t_pos: Target position (grid coordinates).
        """
        GFX.__init__(self)
        self.f_image = []
        surf = pygame.Surface((32, 32), pygame.SRCALPHA, 32)
        pygame.draw.circle(surf, color1, (15, 10), 2, 2)
        pygame.draw.circle(surf, color2, (10, 15), 2, 2)
        pygame.draw.circle(surf, color1, (20, 15), 2, 2)
        self.f_image.append(surf)
        surf = pygame.Surface((32, 32), pygame.SRCALPHA, 32)
        pygame.draw.circle(surf, color2, (15, 10), 2, 2)
        pygame.draw.circle(surf, color1, (10, 15), 2, 2)
        pygame.draw.circle(surf, color1, (20, 15), 2, 2)
        self.f_image.append(surf)
        surf = pygame.Surface((32, 32), pygame.SRCALPHA, 32)
        pygame.draw.circle(surf, color1, (15, 10), 2, 2)
        pygame.draw.circle(surf, color1, (10, 15), 2, 2)
        pygame.draw.circle(surf, color2, (20, 15), 2, 2)
        self.f_image.append(surf)

        self.c = 0
        self.image = self.f_image[self.c]
        self.__pos_gen = self.__pos(s_pos, t_pos)
        self.redraw = False

    def __pos(
        self, s_pos: tuple[int, int], t_pos: tuple[int, int]
    ) -> Generator[tuple[int, int]]:
        """
        Generate positions along a line from start to target.

        Args:
            s_pos: Starting grid position.
            t_pos: Target grid position.

        Yields:
            Pixel coordinates along the path.
        """
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
        """
        Get current surface image for rendering.

        Returns:
            Current pygame Surface for the effect.
        """
        return self.image

    def pos(self) -> tuple[int, int] | None:
        """
        Get current position of the effect.

        Returns:
            Current (x, y) pixel coordinates or None if effect finished.
        """
        try:
            pos = self.__pos_gen.next()
            return pos
        except StopIteration or AttributeError:
            return None
        except Exception as e:
            print(f"Unknown Exception {e} in RayFX.pos()")
            return None

    def tick(self) -> None:
        """Update animation frame."""
        # self.c += 1
        # if self.c >= len(RayFX.f_image):
        #    self.c = 0
        self.c = random.randint(0, len(self.f_image) - 1)
        self.image = self.f_image[self.c]
