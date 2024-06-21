import copy
import os
import random

from actor import Actor
from pdcglobal import (
    DG_BSD,
    F_WALKABLE,
    IF_DRINKABLE,
    IF_IDENTIFIED,
    IF_READABLE,
    MAP_TILE_LIST,
    MT_FLAGS,
    MT_IMAGE,
    MT_INDEX,
    TILESIZE,
    Debug,
    MAP_TILE_down,
    MAP_TILE_up,
    cd,
    d,
)
from pdcresource import Res

VERTICAL = 0
HORIZONTAL = 1


class SADungeon(object):
    game = None

    def __init__(self):
        self.levels = 0
        self.name = "Generic Dungeon"

    def get_map(self, level):
        pass


class DungeonsOfGogadan(SADungeon):
    def __init__(self):
        SADungeon.__init__(self)
        self.levels = 15
        self.name = "Dungeons of Gogadan"

    def __floor_1_2(self, level):
        map = Map.Random(True, True, level, DG_BSD, 40, 40, 4)
        self.game.map = map
        # Populator.fill_map_with_creatures(map, 'test', 15, 25)

        Populator.fill_map_with_items(map, "basic_weapons", 0, 3, 0)
        Populator.fill_map_with_items(map, "basic_stuff", 0, 4, 0)
        # Populator.fill_map_with_items(map, 'basic_books', 0, 2, 99)
        ##Populator.fill_map_with_items(map, 'basic_potions', 0, 2, 99)
        ##Populator.fill_map_with_creatures(map, 'easy_swarms', 0, 2)
        Populator.fill_map_with_creatures(map, "test", 5, 7)
        # Populator.fill_map_with_creatures(map, 'easy_other', 2, 5)
        # Populator.fill_map_with_creatures(map, 'easy_jelly', 0, 3)
        ##Populator.fill_map_with_creatures(map, 'easy_golems', 0, 5)
        return map

    def __floor_3_4(self, level):
        map = Map.Random(True, True, level, DG_BSD, 40, 40, 4)
        self.game.map = map
        Populator.fill_map_with_items(map, "basic_weapons", 1, 3, 12)
        Populator.fill_map_with_items(map, "basic_stuff", 0, 2, 12)
        Populator.fill_map_with_items(map, "basic_books", 0, 1, 99)
        Populator.fill_map_with_items(map, "basic_potions", 1, 4, 99)
        Populator.fill_map_with_creatures(map, "easy_swarms", 1, 2)
        Populator.fill_map_with_creatures(map, "easy_other", 2, 5)
        Populator.fill_map_with_creatures(map, "easy_jelly", 0, 2)
        Populator.fill_map_with_creatures(map, "easy_golems", 1, 2)
        return map

    def __floor_5_6(self, level):
        map = Map.Random(True, True, level, DG_BSD, 60, 60, 5)
        self.game.map = map
        Populator.fill_map_with_items(map, "basic_weapons", 1, 3, 12)
        Populator.fill_map_with_items(map, "basic_stuff", 0, 2, 12)
        Populator.fill_map_with_items(map, "basic_books", 0, 1, 99)
        Populator.fill_map_with_items(map, "basic_potions", 1, 4, 99)
        Populator.fill_map_with_creatures(map, "easy_swarms", 3, 5)
        Populator.fill_map_with_creatures(map, "easy_other", 3, 5)
        Populator.fill_map_with_creatures(map, "easy_jelly", 4, 5)
        Populator.fill_map_with_creatures(map, "easy_golems", 7, 9)
        return map

    def get_map(self, level):
        if level < 3:
            return self.__floor_1_2(level)
        if level < 5:
            return self.__floor_3_4(level)
        if level < 7:
            return self.__floor_5_6(level)


class Populator(object):

    game = None

    def __init__(self):
        pass

    @staticmethod
    def fill_map_with_items(map, filename, min, max, magic):
        stuff = open(os.path.join("item", filename + ".pdcif"), "r").read()
        stuff = stuff.split("\n")

        items = Populator.findAll(stuff)

        count = random.randint(min, max + 1)
        for _ in range(0, count):
            name = random.choice(items)
            item = Populator.__create_item(name, stuff, magic)
            item.set_pos(map.get_random_pos())
            item.filename = filename
            item.pop_name = name
            Populator.game.add_item(item, True)

    @staticmethod
    def create_item(name, filename, magic):
        stuff = open(os.path.join("item", filename + ".pdcif"), "r").read()
        stuff = stuff.split("\n")
        item = Populator.__create_item(name, stuff, magic)
        item.filename = filename
        item.pop_name = name
        return item

    @staticmethod
    def create_creature(name, filename):
        creatures = open(os.path.join("npc", filename + ".pdccf"), "r").read()
        creatures = creatures.split("\n")
        actor = Populator.__create_actor(name, creatures)
        actor.filename = filename
        actor.pop_name = name
        return actor

    @staticmethod
    def fill_map_with_creatures(map, filename, min, max):
        creatures = open(os.path.join("npc", filename + ".pdccf"), "r").read()
        creatures = creatures.split("\n")

        actors = Populator.findAll(creatures)

        count = random.randint(min, max + 1)
        for _ in range(0, count):
            name = random.choice(actors)
            actor = Populator.__create_actor(name, creatures)
            actor.filename = filename
            actor.pop_name = name
            actor.set_pos(map.get_random_pos())
            Populator.game.add_actor(actor, True)
            if hasattr(actor, "swarm"):
                sn, smin, smax, sfile = actor.swarm
                for _ in range(smin, smax):
                    pos = Populator.game.get_free_adj(actor.pos())
                    if pos is None:
                        break
                    Populator.game.add_actor(Populator.create_creature(name, sfile), True)

    @staticmethod
    def __create_item(name, stuff, magic):
        item = None

        sn = True
        br = False
        for index in range(0, len(stuff)):
            if not br:
                line = stuff[index]
                if line.strip() == "":
                    continue
                if line[0] == "#":
                    continue

                if sn:
                    if line[1:] == name:
                        # item = Item(False)
                        # item.flags = IF_IDENTIFIED
                        sn = False
                        continue
                else:
                    if line[0] == "*":
                        br = True
                        continue

                    attr = line.split("=")[0]
                    value = line.split("=")[1]

                    if attr == "type":
                        item = globals()[value](False)
                        # item.type = globals()[value]
                        item.flags = IF_IDENTIFIED
                    elif attr == "img":
                        pos = value.split(":")
                        n = random.randint(0, len(pos) - 1)
                        eq, eq2, dd = pos[n].split(",")
                        item.eq_img = int(eq), int(eq2)
                        item.dd_img = int(dd)
                    elif attr == "damage":
                        no, r = value.split("D")
                        if "+" in r:
                            ey, add = r.split("+")
                        elif "-" in r:
                            ey, add = r.split("-")
                        else:
                            ey, add = r, 0

                        item.damage = value, lambda: cd(int(no), int(ey)) + int(add)
                    elif attr == "name":
                        item.full_name = item.name = value
                    elif attr == "flags":
                        flags = value.split(":")
                        for flag in flags:
                            item.flags |= globals()[flag]
                    elif attr == "av_fx":
                        value = random.choice(value.split(":"))
                        fx, ch = value.split(",")
                        item.av_fx.append((globals()[fx], int(ch)))
                    elif attr == "dv_fx":
                        value = random.choice(value.split(":"))
                        fx, ch = value.split(",")
                        item.dv_fx.append((globals()[fx], int(ch)))
                    elif attr == "iden":
                        value = int(value)
                        if value == 1:
                            if not item.flags & IF_IDENTIFIED:
                                item.flags ^= IF_IDENTIFIED
                    elif attr == "pre" or attr == "suf":
                        if d(100) <= magic:
                            item.special = True
                            if item.flags & IF_IDENTIFIED:
                                item.flags ^= IF_IDENTIFIED
                            p = random.choice(value.split(":"))
                            globals()[p](item)
                            if item.flags & IF_READABLE:
                                if "Read" + p in globals():
                                    item.read = globals()["Read" + p]
                                else:
                                    item.read = suf_books.ReadGenericBook
                            if item.flags & IF_DRINKABLE:
                                item.drink = globals()["Drink" + p]
                    elif attr == "amount":
                        pos = value.split(":")
                        n = random.randint(0, len(pos) - 1)
                        min, max = pos[n].split(",")
                        item.amount += random.randint(int(min), int(max))
                        item.name = str(item.amount) + " " + item.name
                    elif attr == "dt":
                        item.damage_type = globals()[value]
                    elif attr == "info":
                        item.infotext = random.choice(value.split(":"))
                        # str/dex=11/9
                        # enc=1
                        # ap/hp=3/8
                    elif attr == "str/dex":
                        st, dex = value.split("/")
                        item.STR = int(st)
                        item.DEX = int(dex)
                    elif attr == "ap/hp":
                        ap, hp = value.split("/")
                        item.AP = int(ap)
                        item.HP = int(hp)
                    elif attr == "enc":
                        item.ENC = int(value)
                    elif attr == "load":
                        item.load = int(value)
                    elif attr == "range":
                        item.range = int(value)
                        # skill=WT_AXE
                    elif attr == "skill":
                        for skill in value.split(":"):
                            item.skills.append(globals()[skill])
                    elif attr == "locations":
                        locs = value.split(",")
                        for loc in locs:
                            item.locations |= globals()[loc]
                    elif attr == "ap":
                        item.AP = int(value)
                    elif attr == "tsp":
                        item.TSP = int(value)
                    elif attr == "blit_pos":
                        x, y = value.split(",")
                        item.blit_pos = int(x), int(y)
        return item

    @staticmethod
    def __create_actor(name, stuff):
        actor = None

        sn = True
        br = False
        for index in range(0, len(stuff)):
            if not br:
                line = stuff[index]
                if line.strip() == "":
                    continue
                if line[0] == "#":
                    continue

                if sn:
                    if line[1:] == name:
                        actor = Actor(False)
                        sn = False
                        continue
                else:

                    if line[0] == "*":
                        br = True
                        continue

                    attr = line.split("=")[0]
                    value = line.split("=")[1]

                    if attr == "image":
                        value = random.choice(value.split(":"))
                        actor.img_body = int(value), 0
                    elif attr == "speed":
                        pos = value.split(":")
                        n = random.randint(0, len(pos) - 1)
                        actor.speed = actor.cur_speed = int(pos[n])
                    elif attr == "strength":
                        pos = value.split(":")
                        n = random.randint(0, len(pos) - 1)
                        actor.strength = actor.cur_strength = int(pos[n])
                    elif attr == "mind":
                        pos = value.split(":")
                        n = random.randint(0, len(pos) - 1)
                        actor.mind = actor.cur_mind = int(pos[n])
                    elif attr == "endurance":
                        pos = value.split(":")
                        n = random.randint(0, len(pos) - 1)
                        actor.endurance = actor.cur_endurance = int(pos[n])
                    elif attr == "ai":
                        ai_class = globals()[value]
                        actor.ai = ai_class(actor)
                    elif attr == "name":
                        actor.name = value
                    elif attr == "hp":
                        min, max = value.split(",")
                        actor.health = actor.cur_health = random.randint(int(min), int(max))
                    elif attr == "natural_av":
                        value = random.choice(value.split(":"))
                        actor.natural_av = int(value)
                    elif attr == "natural_dv":
                        value = random.choice(value.split(":"))
                        actor.natural_dv = int(value)
                    elif attr == "dv_fx":
                        value = random.choice(value.split(":"))
                        fx, ch = value.split(",")
                        actor.dv_fx.append((globals()[fx], int(ch)))
                    elif attr == "av_fx":
                        value = random.choice(value.split(":"))
                        fx, ch = value.split(",")
                        actor.av_fx.append((globals()[fx], int(ch)))
                    elif attr == "corpse":
                        actor.ch_drop_corpse = int(value)
                    elif attr == "gold":
                        min, max = value.split(",")
                        actor.gold = random.randint(int(min), int(max) + 1)
                    elif attr == "swarm":
                        n, min, max, file = value.split(",")
                        actor.swarm = n, int(min), int(max), file
                    elif attr == "weapon":
                        value = random.choice(value.split(":"))
                        item, file, magic = value.split(",")
                        weap = Populator.create_item(item, file, magic)
                        actor.weapon = weap
                        actor.items.append(weap)
                    elif attr == "items":
                        value = random.choice(value.split(":"))
                        item, file, magic = value.split(",")
                        actor.items.append(Populator.create_item(item, file, magic))
                    elif attr == "xp_value":
                        actor.xp_value = int(value)
                    elif attr == "morale":
                        actor.morale = int(random.choice(value.split(":")))
        return actor

    @staticmethod
    def findAll(stuff):
        actors = []
        for line in stuff:
            if line.strip() == "" or line.startswith("#"):
                continue
            if line[0] == "*":
                actors.append(line[1:])
        return actors


testmap = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 9, 9, 9, 9, 9, 9, 9, 9],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9],
]


class Map(object):

    tiles = None
    game = None

    def __init__(self, MapArray, level=1):
        self.game.add_to_world_objects(self)
        self.map_array = []

        for line in MapArray:
            new_line = []
            for tile in line:
                nt = (mt for mt in MAP_TILE_LIST if mt[MT_INDEX] == tile).next()
                new_line.append(copy.copy(nt))
            self.map_array.append(new_line)

        self.height = len(MapArray)
        self.width = len(MapArray[0])
        self.cur_surf = None
        self.level = level
        Debug.debug("Map is " + str(self.width) + "x" + str(self.height))

    def check_tiles(self):
        if Map.tiles is None:
            Map.tiles = Res("dc-dngn.png", TILESIZE)

    def clear_surfaces(self):
        Map.Tiles = None
        self.cur_surf = None

    @staticmethod
    def Random(up=True, down=True, level=1, type=DG_BSD, w=80, h=40, s=5):
        #        startx = 90
        #        starty = 100
        #        somename = dMap()
        #        #size 50 x 50, a low (10) chance of making new rooms with a 50% chance new rooms will be corridors,
        #        #and a maximum of 20 rooms.
        #        somename.makeMap(startx, starty, 10, 40, 35)
        #        array = []
        #        for y in range(0, starty):
        #            line = []
        #            for x in range(0, startx):
        #                if somename.mapArr[y][x] == 0: #floor
        #                    line.append(0)
        #                if somename.mapArr[y][x] == 1: #void
        #                    line.append(9)
        #                if somename.mapArr[y][x] == 2: #wall
        #                    line.append(1)
        #                #door
        #                if somename.mapArr[y][x] == 3 or somename.mapArr[y][x] == 4 or somename.mapArr[y][x] == 5:
        #                    line.append(2)
        #            array.append(line)

        if type == DG_BSD:
            #! LOOK AWAY!! BAD, BAD CODE!!
            i = 0
            array = None
            r1 = bsd.Room(0, 0, w, h)
            bsd.split(r1, s)
            while array is None and i < 20:
                i += 1
                try:
                    array = bsd.create(r1)
                except Exception:
                    array = None
                    r1 = bsd.Room(0, 0, w, h)
                    bsd.split(r1, s)

            if array is None:
                raise "Argh!! Bad code rising!"

            for y in range(len(array)):
                for x in range(len(array[0])):
                    if array[y][x] == ".":
                        array[y][x] = 1
                    if array[y][x] == "*":
                        array[y][x] = 0

        #        c=cave_gen(100,50,4)
        #        c.fix()
        #        array=c.A
        #
        #        for y in range(len(array)):
        #            for x in range(len(array[0])):
        #                if array[y][x] == 1:
        #                    array[y][x] = 9
        #                if array[y][x] == 0:
        #                    array[y][x] = -1

        map = Map(array, level)
        if down:
            x, y = map.get_random_pos()
            map.map_array[y][x] = MAP_TILE_down
        if up:
            x, y = map.get_random_pos()
            map.map_array[y][x] = MAP_TILE_up

        return map

    def get_random_pos(self):
        pos = None
        while pos is None:
            y = random.randint(0, self.height - 1)
            x = random.randint(0, self.width - 1)
            Debug.debug("get random pos: " + str(x) + " " + str(y))
            if self.map_array[y][x][MT_FLAGS] & F_WALKABLE:
                pos = x, y
        return x, y

    def can_enter(self, pos, move_mode):

        target_tile = self.map_array[pos[1]][pos[0]]
        if target_tile[MT_FLAGS] & move_mode:
            return True

        return False

    def get_tile_at(self, x, y):
        self.check_tiles()
        # if self.map_array[y][x][MT_IMAGE] == 3:
        #    print('sdasd')
        img = self.tiles.get(self.map_array[y][x][MT_IMAGE])
        return img


class tool:

    # TODO verify indentation correction is accurate
    @staticmethod
    def line(x, y, x2, y2):
        """
        Brensenham line algorithm
        """

        steep = 0
        coords = []

        dx = abs(x2 - x)
        if (x2 - x) > 0:
            sx = 1
        else:
            sx = -1

        dy = abs(y2 - y)
        if (y2 - y) > 0:
            sy = 1
        else:
            sy = -1

        if dy > dx:
            steep = 1
            x, y = y, x
            dx, dy = dy, dx
            sx, sy = sy, sx
            d = (2 * dy) - dx

        for i in range(0, dx):
            if steep:
                coords.append((y, x))
            else:
                coords.append((x, y))

        while d >= 0:
            y = y + sy
            d = d - (2 * dx)
            x = x + sx
            d = d + (2 * dy)
            coords.append((x2, y2))

        return coords


class cave_gen:

    def __init__(self, WIDTH, HEIGHT, count=0):
        self.width = WIDTH
        self.height = HEIGHT

        A = []
        for i in range(self.height):
            A.append([0] * self.width)

        for y in range(self.height):
            for x in range(self.width):
                if random.randrange(100) <= 45:
                    tile = 1
                else:
                    tile = 0

                A[y][x] = tile
        self.A = A

        if count > 1:
            self.apply_cell(count)

    def polycut(self):
        x1 = random.randrange(0, self.width / 4)
        y1 = random.randrange(0, self.height / 4)

        x2 = random.randrange(self.width - self.width / 4, self.width)
        y2 = random.randrange(0, self.height / 4)

        x3 = random.randrange(0, self.width / 4)
        y3 = random.randrange(self.height - self.height / 4, self.height)

        x4 = random.randrange(self.width - self.width / 4, self.width)
        y4 = random.randrange(self.height - self.height / 4, self.height)

        lines = []
        lines.append(tool.line(x1, y1, x2, y2))
        lines.append(tool.line(x2, y2, x3, y3))
        lines.append(tool.line(x3, y3, x4, y4))
        lines.append(tool.line(x4, y4, x1, y1))

        for line in lines:
            for point in line:
                x, y = point
                self.A[y][x] = 0

    def apply_cell(self, count):

        for _ in range(count):

            # A = self.A
            B = []
            for i in range(self.height):
                B.append([0] * self.width)

            for y in range(self.height):
                for x in range(self.width):
                    if self.checkn(y, x, 4) or self.checkopen(y, x):
                        B[y][x] = 1
            self.A = B

    def checkopen(self, y, x):
        A = self.A
        wn = 0
        for r_x in (-2, -1, 0, 1, 2):
            for r_y in (-2, -1, 0, 1, 2):
                b_x = x + r_x
                b_y = y + r_y
                try:
                    if A[b_y][b_x]:
                        wn += 1
                except IndexError:
                    pass
                except Exception as e:
                    print(f"Unexpected Exception {e} in cg.py checkopen()")
        if wn == 0:
            return 1
        else:
            return 0

    def checkn(self, y, x, n):
        A = self.A
        wn = 0
        for r_x in (-1, 0, 1):
            for r_y in (-1, 0, 1):
                b_x = x + r_x
                b_y = y + r_y
                try:
                    if A[b_y][b_x]:
                        wn += 1
                except IndexError:
                    pass
                except Exception as e:
                    print(f"Unexpected Exception {e} in cg.py checkn()")
        if wn > n:
            return 1
        else:
            return 0

    def dprint(self):

        A = self.A
        z = ""
        i = []
        for y in range(self.height):
            for x in range(self.width):
                if A[y][x] == 1:
                    z += "#"
                elif A[y][x] == 3:
                    z += "@"
                else:
                    z += "."
                # z+=str(A[y][x])
            i.append(z)
            z = ""

        for y in range(self.height):
            print(i[y])

    def fix(self):
        A = self.A
        N = []
        for y in range(self.height + 1):
            lines = []
            for x in range(self.width + 1):
                lines.append(".")
            N.append(lines)

        for y in range(self.height + 1):
            for x in range(self.width + 1):
                if y == 0 or x == 0 or y == self.height - 1 or x == self.width - 1:
                    N[y][x] = 1
                else:
                    N[y][x] = A[y - 1][x - 1]
        self.A = N

    def dget(self):

        A = self.A
        z = ""
        i = []
        for y in range(self.height):
            for x in range(self.width):
                if A[y][x] == 1:
                    z += "#"
                else:
                    z += "."
                # z+=str(A[y][x])
            i.append(z)
            z = ""

        return i


class Room(object):
    def __init__(self, x, y, w, h):
        self.childs = None
        self.sibling = None
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rx = x + random.randint(1, 4)
        self.ry = y + random.randint(1, 4)

        self.rh = h - random.randint(1, 4)
        while self.rh - self.ry < 3:
            self.rh += 1

        self.rw = w - random.randint(1, 4)
        while self.rw - self.rx < 3:
            self.rw += 1

        self.split = None
        self.parent = None
        self.corridor = False


def split_room(room, vertical):
    # if room.parent is not None:
    #    if room.parent.parent is not None:
    #        if random.randint(0, 100) < 10:
    #            return

    if vertical:
        split_line = (room.w - room.x) / 2 + random.randint(-3, 3)
        room1 = Room(room.x, room.y, room.x + split_line, room.h)
        room2 = Room(room.x + split_line, room.y, room.w, room.h)
    else:
        split_line = (room.h - room.y) / 2 + random.randint(-3, 3)
        room1 = Room(room.x, room.y, room.w, room.y + split_line)
        room2 = Room(room.x, room.y + split_line, room.w, room.h)
    room.split = vertical
    room1.parent = room
    room2.parent = room

    room.childs = [room1, room2]
    room1.sibling = room2
    room2.sibling = room1


def split(room, count):
    rooms = [room]
    for _ in range(count):
        new = []
        for r in rooms:
            if r.parent is not None:
                split = not r.parent.split
            else:
                split = random.choice((True, False))
            split_room(r, split)
            if r.childs is not None:
                new.extend(r.childs)
        rooms = []
        rooms.extend(new)


def connect_rooms(rooms, map_array, sy="*"):
    for r in rooms:
        # if r==None: return
        # if r.parent==None:continue
        if r.corridor:
            continue
        vert = r.parent.split

        if vert:
            s = r.sibling
            mm1 = max(r.ry + 1, s.ry + 1)
            mm2 = min(r.rh - 1, s.rh - 1)

            if mm1 != mm2:
                y = random.randint(mm1, mm2)
            else:
                y = mm1
            if r.x < s.x:
                v = r.rx + 1
                b = s.rx + 1
            else:
                v = s.rx + 1
                b = r.rx + 1

            while map_array[y][v] == ".":
                v += 1

            while map_array[y][b - 1] == ".":
                b += 1

            for x in range(v, b - 1):
                map_array[y][x] = sy
            r.corridor = s.corridor = True
        else:
            s = r.sibling
            mm1 = max(r.rx + 1, s.rx + 1)
            mm2 = min(r.rw - 1, s.rw - 1)

            if mm1 != mm2:
                x = random.randint(mm1, mm2)
            else:
                x = mm1

            if r.y < s.y:
                v = r.ry
                b = s.ry + 1
            else:
                v = s.ry
                b = r.ry + 1

            while map_array[v][x] == ".":
                v += 1

            while map_array[b - 1][x] == ".":
                b += 1

            for y in range(v, b - 1):
                map_array[y][x] = "*"
            r.corridor = s.corridor = True


def get_all_rooms(room):
    rooms = [room]
    finish = False

    while not finish:
        new = []
        finish = True
        for r in rooms:
            if r.childs is not None:
                new.extend(r.childs)
                finish = False
            else:
                new.append(r)
        if not finish:
            rooms = []
            rooms.extend(new)
    return rooms


def create(room):
    rooms = get_all_rooms(room)
    map_array = []
    for _ in range(room.h):
        line = []
        for _ in range(room.w):
            line.append(".")
        map_array.append(line)

    for r in rooms:
        for y in range(r.ry, r.rh):
            for x in range(r.rx, r.rw):
                map_array[y][x] = "*"

    connect_rooms(rooms, map_array)
    parents = set()
    [parents.add(r.parent) for r in rooms]
    #
    while len(parents) > 1:
        connect_rooms(parents, map_array)
        new = set()
        for r in parents:
            if r.parent is not None:
                new.add(r.parent)
        parents = new

    A = map_array
    N = []
    for y in range(room.h + 1):
        array = []
        for x in range(room.w + 1):
            array.append(".")
        N.append(array)

    for y in range(room.h + 1):
        for x in range(room.w + 1):
            if y == 0 or x == 0 or y == room.h - 1 or x == room.w - 1:
                N[y][x] = 1
            else:
                N[y][x] = A[y - 1][x - 1]
    map_array = N

    return map_array


if __name__ == "__main__":
    r1 = Room(0, 0, 100, 50)
    split(r1, 5)
    map_array = create(r1)
    for line in map_array:
        item = ""
        for s in line:
            item = item + str(s)
        print(item)
