import random

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
    d,
    line,
)
from pdcresource import Res


class GFX(object):
    game = None

    def __init__(self):
        self.redraw = True
        self.xoff = 0
        self.yoff = 0

    def get_surf(self):
        pass

    def pos(self):
        pass

    def tick(self):
        pass


class ProjectileFX(GFX):

    rescache = None

    def __init__(self, dir, s_pos, t_pos, type="Arrow"):
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

        self.image = self.rescache.get(img)

        self.__pos_gen = self.__pos(s_pos, t_pos)
        self.redraw = True

    def __pos(self, s_pos, t_pos):
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

    def get_surf(self):
        return self.image

    def pos(self):
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


class BallFX(GFX):
    def __init__(self, color1, color2, s_pos, t_pos, radius=1):
        GFX.__init__(self)
        self.f_image = []
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
        self.lastpos = None

    def __pos(self, s_pos, t_pos):
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

    def get_surf(self):
        return self.image

    def pos(self):
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
        else:
            if not self.finish:
                return self.lastpos[0] + self.xoff, self.lastpos[1] + self.yoff
            else:
                return None

    def tick(self):
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
            if int(self.cur_radius) < width:
                width = int(self.cur_radius)
            pygame.draw.circle(self.image, color, (max_size, max_size), int(self.cur_radius), width)

            self.cur_radius += 4

            # size = (float(self.cur_radius) + 0.5) * TILESIZE
            self.xoff = -TILESIZE * self.radius
            self.yoff = -TILESIZE * self.radius
            if self.cur_radius >= max_size:
                self.finish = True


class RayFX(GFX):
    def __init__(self, color1, color2, s_pos, t_pos):
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

    def __pos(self, s_pos, t_pos):
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

    def get_surf(self):
        return self.image

    def pos(self):
        try:
            pos = self.__pos_gen.next()
            return pos
        except StopIteration or AttributeError:
            return None
        except Exception as e:
            print(f"Unknown Exception {e} in RayFX.pos()")
            return None

    def tick(self):
        # self.c += 1
        # if self.c >= len(RayFX.f_image):
        #    self.c = 0
        self.c = random.randint(0, len(self.f_image) - 1)
        self.image = self.f_image[self.c]


class ThrowFX(GFX):

    rescache = None

    def __init__(self, dir, s_pos, t_pos, item):
        GFX.__init__(self)

        self.image = item.get_dd_img()

        self.__pos_gen = self.__pos(s_pos, t_pos)
        self.redraw = True

    def __pos(self, s_pos, t_pos):
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

    def get_surf(self):
        return self.image

    def pos(self):
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
