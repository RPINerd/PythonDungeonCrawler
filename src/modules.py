import copy
import os
import random

import pygame

from key_mapping import (
    MOVE_DOWN,
    MOVE_DOWN_LEFT,
    MOVE_DOWN_RIGHT,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    MOVE_UP_LEFT,
    MOVE_UP_RIGHT,
    MOVE_WAIT,
    MOVES,
)
from pdcglobal import (
    BLACK,
    BLUE,
    D_ACID,
    D_CHAOS,
    D_COLD,
    D_FIRE,
    D_GENERIC,
    D_ORDER,
    D_POISON,
    DG_BSD,
    F_WALKABLE,
    GREEN,
    I_AMMO,
    I_ARMOR,
    I_BOOTS,
    I_CORPSE,
    I_GOLD,
    I_HELMET,
    I_SHIELD,
    I_STUFF,
    I_TROUSERS,
    I_VOID,
    I_WEAPON,
    IF_DRINKABLE,
    IF_EATABLE,
    IF_FIRES_DART,
    IF_IDENTIFIED,
    IF_MELEE,
    IF_RANGED,
    IF_READABLE,
    IF_SHIELD,
    L_ABDOMEN,
    L_ARMS,
    L_CHEST,
    L_HEAD,
    L_LEGS,
    MAP_TILE_LIST,
    MM_WALK,
    MT_FLAGS,
    MT_IMAGE,
    MT_INDEX,
    PURPLE,
    RED,
    ST_GENERIC,
    ST_ORDER,
    TILESIZE,
    WHITE,
    WT_UNARMED,
    YELLOW,
    Debug,
    MAP_TILE_down,
    MAP_TILE_up,
    ammo_fits_weapon,
    cd,
    d,
    get_combat_actions,
    get_damage_mod,
    get_dis,
    get_new_pos,
    r2d6,
    r4d6,
)
from pdcresource import Res

VERTICAL = 0
HORIZONTAL = 1


class Actor(object):

    tiles = None
    game = None

    def __init__(self, add):
        Debug.debug("Creating Actor")
        self.game.add_actor(self, add)
        self.name = "Generic Actor"
        self.cur_surf = None
        self.img_body = None
        self.id = self.game.get_id()
        self.sc = None

        self.timer = 0

        self.x = 1
        self.y = 1

        self.morale = 75

        self.move_mode = MM_WALK

        self.timer = 0
        self.ai = AI(self)

        self.gold = 0
        self.xp_value = 25
        self.xp = 0

        self.STR = r4d6()
        self.CON = r4d6()
        self.DEX = r4d6()
        self.SIZ = r2d6()
        self.INT = r2d6()
        self.POW = r4d6()
        self.CHA = r4d6()
        self.MOVE = 4
        self.calc_stats()

        self.check_tiles()

        self.items = []
        self.spells = []

        self.av_fx = []
        self.dv_fx = []
        self.running_fx = []

        self.ch_drop_corpse = 33

        self.classkit = None
        self.dazzled = False

        self.armor = []
        self.weapon = None
        self.ammo = None
        self.unarmed_weapon = Unarmed(False)
        self.unconscious = False
        self.prone = False

    def calc_stats(self):
        self.CA = get_combat_actions(self.DEX)
        self.cur_CA = self.CA
        self.RA = self.CA
        self.cur_RA = self.RA
        self.DM = get_damage_mod(self.STR + self.SIZ)
        self.MP = self.POW
        self.SR = (self.INT + self.DEX) / 2
        self.HP = HitZones(self)
        self.hit_zones = HitZones(self)
        self.useless_zones = set()
        self.major_wounds = {}
        self.skills = Skills(self)

    def get_STR(self):
        return self.STR

    def get_CON(self):
        return self.CON

    def get_DEX(self):
        return self.DEX

    def get_SIZ(self):
        return self.SIZ

    def get_INT(self):
        return self.INT

    def get_POW(self):
        return self.POW

    def get_CHA(self):
        return self.CHA

    def get_DM(self):
        return self.DM

    def get_CA(self):
        return self.cur_CA

    def get_RA(self):
        return self.cur_RA

    def get_MOVE(self):
        return self.MOVE

    def gain_xp(self, amount):
        """The Actor's XP increases by the given amount"""
        self.xp += amount

    def get_av_fx(self):
        """Returns all Effects the Actor can trigger when attacking"""
        fx = [f for f in self.av_fx]
        for item in self.get_equipment():
            for f in item.av_fx:
                fx.append(f)
        return fx

    def get_dv_fx(self):
        """Returns all Effects the Actor can trigger when being attacked"""
        fx = [f for f in self.dv_fx]
        for item in self.get_equipment():
            for f in item.dv_fx:
                fx.append(f)
        return fx

    def redraw(self):
        """Clears the Surface so the image of the Actor will be redrawn"""
        self.cur_surf = None

    def clear_surfaces(self):
        """Set's all Surfaces to None to prevent Surface.Quit-Errors after unpickling"""
        for item in self.items:
            item.clear_surfaces()
        self.cur_surf = None
        Actor.tiles = None

    def go_prone(self, instantly=False):
        self.prone = True
        if not instantly:
            self.timer += 100 - self.get_MOVE() * 2

    def fall_unconscious(self):
        self.unconscious = True

    # TODO for c,m,s,l below, figure out better names
    def serious_wound(self, zone):
        c, m, s, l = getattr(self.HP, zone)
        self.game.shout("%s has a serious wounded %s" % (self.name, s))

        for _ in range(d(4)):
            self.timer += 100 - self.get_MOVE() * 2

        if zone == "R_Arm":
            item = self.weapon
            if item is not None:
                self.take_off(item, instantly=True)
                self.drop(item, instantly=True)

        if zone == "L_Arm":
            item = self.weapon
            if item is not None and item.H2:
                self.take_off(item, instantly=True)
                self.drop(item, instantly=True)
            for item in self.get_equipment():
                if item.type == IF_SHIELD:
                    self.take_off(item, instantly=True)
                    self.drop(item, instantly=True)
                    break

        if zone in ("L_Leg", "R_Leg"):
            self.go_prone(instantly=True)

        if zone in ("Abdomen", "Chest", "Head"):
            if d(100) > self.skills.Resilence:
                self.fall_unconscious()

        self.useless_zones.add(zone)

    def major_wound(self, zone):
        c, m, s, l = getattr(self.HP, zone)
        self.game.shout("%s has a major wounded %s" % (self.name, s))

        if zone in ("R_Arm", "L_Arm", "L_Leg", "R_Leg"):
            if d(100) > self.skills.Resilence:
                self.fall_unconscious()
            self.go_prone(instantly=True)
            self.serious_wound(zone)
            self.major_wounds[zone] = self.CON + self.POW

        if zone in ("Abdomen", "Chest", "Head"):
            if d(100) > self.skills.Resilence:
                self.die()
            if d(100) > self.skills.Resilence:
                self.fall_unconscious()
            self.major_wounds[zone] = (self.CON + self.POW) / 2

        self.useless_zones.add(zone)

    def minor_wound(self, zone):
        c, m, s, l = getattr(self.HP, zone)
        self.game.shout("%s has a minor wounded %s" % (self.name, s))
        self.timer += 100 - self.get_MOVE() * 2

    def do_damage(self, dam, zone, type):
        """
        The Actor suffers the given amount of Damage
        """

        if self.game.player == self:
            self.game.redraw_stats()

        cur_hp, max_hp, zone_desc, zone_flag = getattr(self.HP, zone)

        armors = [item for item in self.get_equipment() if item.locations & zone_flag]
        if len(armors) > 0:
            armors.sort(cmp=lambda x, y: y.AP - x.AP)
            dam = max(dam - armors[0].AP, 0)
            Debug.debug("%s reduces damage" % (armors[0].name))
            if dam == 0:
                return 0

        cur_hp -= dam
        setattr(self.HP, zone, (cur_hp, max_hp, zone_desc, zone_flag))

        if cur_hp == 0:
            self.minor_wound(zone)
        elif cur_hp < 0 and cur_hp > -max_hp:
            self.serious_wound(zone)
        elif cur_hp < 0:
            self.major_wound(zone)

        return dam

    def read(self, item):
        """
        The Actor reads the given Item
        """
        self.timer += 100 - self.get_INT() * 2
        item.read(item, self)

    def drink(self, item):
        """
        The Actor drinks the given Item
        """
        self.items.remove(item)
        self.game.free_symbol(item.player_symbol)
        item.player_symbol = None
        self.game.del_item(item)
        self.timer += 100
        item.drink(item, self)

    def equip(self, item):
        if item.type == I_ARMOR:
            self.armor.append(item)
        if item.type == I_WEAPON:
            if self.weapon is not None:
                self.weapon.equipped = False
            self.weapon = item

        if item.type == I_AMMO:
            if self.ammo is not None:
                self.ammo.equipped = False
            self.ammo = item

        self.timer += 200 - self.get_DEX() * 2
        Debug.debug("%s equipped %s" % (self.name, item.get_name()))
        item.equipped = True
        self.redraw()
        return True

    def take_off(self, item, instantly=False):
        if not instantly:
            self.timer += 200 - self.get_DEX() * 2
        item.equipped = False
        if item.type == I_ARMOR:
            self.armor.remove(item)
        if item.type == I_WEAPON:
            self.weapon = None
        if item.type == I_AMMO:
            self.ammo = None
        self.redraw()
        Debug.debug("%s took off %s" % (self.name, item.get_name()))

    def drop(self, item, instantly=False):
        self.items.remove(item)
        self.game.add_item(item)
        item.picked_up = False
        if not instantly:
            self.timer += max(50 - self.DEX * 2, 0)
        self.game.free_symbol(item.player_symbol)
        item.player_symbol = None

    def throw(self, item, pos):
        item.equipped = False
        item.picked_up = False
        self.game.add_item(item)
        if item == self.weapon:
            self.weapon = None
            self.redraw()
        self.items.remove(item)
        self.game.throw_item(self, item, pos)

    def fire(self, pos):
        self.timer += 100 * (5 - self.get_CA())
        if not self.ammo.used():
            self.items.remove(self.ammo)
            self.game.del_item(self.ammo)
        self.game.range_attack(self, pos)

    def cast(self, spell):
        if self.cur_endurance < spell.phys_cost:
            return False
        if self.mind < spell.mind_cost:
            return False
        self.cur_endurance -= spell.phys_cost
        self.cur_mind -= spell.mind_cost
        self.timer += 100 * (5 - self.get_CA())
        return spell.cast(self)

    def get_equipment(self):
        return [item for item in self.items if item.equipped]

    def pick_up(self, item):
        self.timer += max(100 - self.DEX * 2, 0)
        symbol = item.get_ps()
        if item.type == I_GOLD:
            self.gold += item.amount
            self.game.free_symbol(symbol)
        else:
            stacked = False
            if item.amount > 0:
                lines = []
                lines.extend(self.get_equipment())
                lines.extend(self.items)
                for i in lines:
                    if item.pop_name == i.pop_name:
                        i.amount += item.amount
                        stacked = True
                        self.game.free_symbol(symbol)
                        break
            if not stacked:
                self.items.append(item)
                if self == self.game.player:
                    # item.player_symbol = self.game.get_symbol()
                    self.game.shout("You picked up a %s" % (item.get_name()))
                else:
                    self.game.free_symbol(symbol)

        self.game.del_item(item)
        item.picked_up = True
        Debug.debug("%s picked up %s" % (self.name, item.get_name()))

    def check_tiles(self):
        if Actor.tiles is None:
            Actor.tiles = Res("dc-mon.png", TILESIZE)

    def die(self, text=None):
        self.game.del_actor(self)
        if d(100) < self.ch_drop_corpse:
            self.__drop_corpse()
        for item in self.get_equipment():
            self.take_off(item)
            self.drop(item)
        for item in self.items:
            self.drop(item)
        if self.gold > 0:
            self.game.create_gold(self.gold, self.pos())
        if text is None:
            self.game.shout("%s dies" % (self.name))
        else:
            self.game.shout("%s dies of %s" % (self.name, text))
        if self.game.player == self:
            self.game.game_over()

    def __drop_corpse(self):
        Corpse(self)

    def equip_melee(self):
        melee_weapons = []
        if self.slot.weapon.flags & IF_MELEE:
            melee_weapons.append(self.slot.weapon)
        for item in self.items:
            if item.flags & IF_MELEE:
                melee_weapons.append(item)
        if len(melee_weapons) > 0:
            # melee_weapons.sort(cmp=lambda x, y: y.av - x.av)
            weapon = melee_weapons[0]
            if weapon.type != I_VOID:
                self.equip(weapon)
            else:
                self.take_off(self.slot.weapon)

    def equip_range(self):
        range_weapons = []

        for item in self.items:
            if item.flags & IF_RANGED:
                range_weapons.append(item)

        ammos = []
        for item in self.items:
            if item.type == I_AMMO:
                ammos.append(item)

        for weapon in range_weapons:
            for ammo in ammos:
                if ammo_fits_weapon(ammo, weapon):
                    # ((ammo.flags & IF_ARROW and weapon.flags & IF_FIRES_ARROW) or
                    #    (ammo.flags & IF_BOLT and weapon.flags & IF_FIRES_BOLT)):
                    if weapon.type != I_VOID:
                        self.equip(weapon)
                    else:
                        self.take_off(self.slot.weapon)
                    self.equip(ammo)
                    return

    def melee_equipped(self):
        weapon = self.weapon
        melee_weapons = []
        for item in self.items:
            if item.flags & IF_MELEE:
                melee_weapons.append(item)

        if weapon is None:
            if len(melee_weapons) > 0:
                return False
            else:
                return True

        if weapon.flags & IF_MELEE:
            return True

        return False

    def range_equipped(self):
        weapon = self.weapon
        if self.weapon is None:
            return False
        if weapon.flags & IF_RANGED:
            ammo = self.ammo
            if ammo is None:
                return False
            if ammo_fits_weapon(ammo, weapon):
                return True
        return False

    def ready_to_range(self):
        range_weapons = []

        for item in self.items:
            if item.flags & IF_RANGED:
                range_weapons.append(item)

        ammos = []
        if self.ammo is not None:
            ammos.append(self.ammo)

        for item in self.items:
            if item.__class__.__name__ == "Ammo":
                ammos.append(item)

        for weapon in range_weapons:
            for ammo in ammos:
                if ammo_fits_weapon(ammo, weapon):
                    # ((ammo.flags & IF_ARROW and weapon.flags & IF_FIRES_ARROW) or
                    #    (ammo.flags & IF_BOLT and weapon.flags & IF_FIRES_BOLT)):
                    return True

        return False

    def get_body_tile(self):
        surf = pygame.Surface((TILESIZE, TILESIZE))  # , pygame.SRCALPHA, 32)
        surf.blit(self.tiles.get_subs(self.img_body), (0, 0))
        return surf

    def get_tile(self):

        self.check_tiles()

        surf = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA, 32)

        surf.blit(self.tiles.get_subs(self.img_body), (0, 0))

        # if self.armor is not None:
        #    surf.blit(self.armor.get_eq_img(), (TILESIZE / 4, 0))
        if self.weapon is not None:
            surf.blit(self.weapon.get_eq_img(), self.weapon.blit_pos)

        for armor in self.armor:
            surf.blit(armor.get_eq_img(), armor.blit_pos)
            (TILESIZE / 2, 0)
        # surf.blit(self.slot.weapon.get_eq_img(), (0, 0))
        # surf.blit(self.slot.head.get_eq_img(), (TILESIZE / 4, 0))

        return surf

    def pos(self):
        return self.x, self.y

    def set_pos(self, pos):
        self.game.update_actor_pos(self, pos)
        self.x = pos[0]
        self.y = pos[1]
        [item.set_pos(self.pos()) for item in self.items]

    def tick(self):

        self.dazzled = False
        # self.useless_zones = set()
        # self.major_wounds = {}
        for zone in self.useless_zones:
            if zone in ("Abdomen", "Chest", "Head"):
                if d(100) > self.skills.Resilence:
                    self.fall_unconscious()

        for zone in self.major_wounds.keys():
            if self.major_wounds[zone] == 0:
                self.die("bloodloss and internal injuries")
                break
            else:
                if zone in ("Abdomen", "Chest", "Head"):
                    if d(100) > self.skills.Resilence:
                        self.die("bloodloss and internal injuries")
                        break
                    if d(100) > self.skills.Resilence:
                        self.fall_unconscious()
                else:
                    if d(100) > self.skills.Resilence:
                        self.fall_unconscious()

                self.major_wounds[zone] -= 1

        for e in self.running_fx:
            e.tick()

    def act(self):
        self.cur_RA = self.RA
        if not self.unconscious:
            if self.ai is not None:
                self.ai.act()
        else:
            self.move(MOVE_WAIT)
            self.game.shout("%s is unconscious" % (self.name))

    def opposite_dir(self, target):
        if hasattr(target, "x"):
            tx = target.x
            ty = target.y
        else:
            tx = target[0]
            ty = target[1]

        if self.x > tx:
            if self.y == ty:
                move_d = MOVE_RIGHT
            elif self.y > ty:
                move_d = MOVE_DOWN_RIGHT
            else:
                move_d = MOVE_UP_RIGHT

        if self.x < tx:
            if self.y == ty:
                move_d = MOVE_LEFT
            elif self.y > ty:
                move_d = MOVE_DOWN_LEFT
            else:
                move_d = MOVE_UP_LEFT

        if self.x == tx:
            if self.y > ty:
                move_d = MOVE_DOWN
            else:
                move_d = MOVE_UP

        return move_d

    def locateDirection(self, target):
        """Checks in what direction the target is"""

        if hasattr(target, "x"):
            tx = target.x
            ty = target.y
        else:
            tx = target[0]
            ty = target[1]

        if self.x > tx:
            if self.y == ty:
                move_d = MOVE_LEFT
            elif self.y > ty:
                move_d = MOVE_UP_LEFT
            else:
                move_d = MOVE_DOWN_LEFT

        if self.x < tx:
            if self.y == ty:
                move_d = MOVE_RIGHT
            elif self.y > ty:
                move_d = MOVE_UP_RIGHT
            else:
                move_d = MOVE_DOWN_RIGHT

        if self.x == tx:
            if self.y > ty:
                move_d = MOVE_UP
            else:
                move_d = MOVE_DOWN

        return move_d

    def move(self, direction):
        if direction == MOVE_WAIT:
            self.timer += 100 - self.get_MOVE() * 2
            return True

        new_pos = get_new_pos(self.pos(), direction)

        result = self.game.is_move_valid(self, new_pos)

        if result:
            self.set_pos(new_pos)
            self.timer += 100 - self.get_MOVE() * 2
            return True

        if isinstance(result, Actor):
            if result != self:
                if result.id in self.ai.friends:
                    if self == self.game.player:
                        result.set_pos(self.pos())
                        self.set_pos(new_pos)
                        self.timer += 100 - self.get_MOVE() * 2
                        result.timer += 100 - result.get_MOVE() * 2
                        self.game.shout("You displaced %s" % (result.name))
                        self.sc.do_fov(self.x, self.y, 15)
                        return True
                    else:
                        return False
                self.game.attack(self, result)
                self.timer += 100 * (5 - self.get_CA())
                return result

        return False


class AI(object):
    game = None

    def __init__(self, actor):
        self.actor = actor
        self.hostile = set()
        self.friends = set()

    def act(self):
        pass

    def get_all_foes_in_sight(self):
        all_foes = self.game.get_all_srd_actors(self.actor.pos(), radius=15)
        seeing = []
        self.actor.sc.do_fov(self.actor.x, self.actor.y, 10)
        for act in all_foes:
            x, y = act.pos()
            if self.actor.sc.lit(x, y) and act.id in self.hostile:  # not act.id in self.friends:
                seeing.append(act)
        return seeing

    def seeing_actor(self, target):
        dis = get_dis(self.actor.x, self.actor.y, target.x, target.y)
        if dis > 15:
            return False

        self.actor.sc.do_fov(self.actor.x, self.actor.y, 10)
        x, y = target.pos()
        return self.actor.sc.lit(x, y)

    def seeing_player(self):
        return self.seeing_actor(self.game.player)

    def get_player_direction(self):
        return self.actor.locateDirection(self.game.player)

    def build_alternate_dirs(self, dir, panic=False):
        if dir == MOVE_UP:
            return [MOVE_UP_LEFT, MOVE_UP_RIGHT] if not panic else [MOVE_UP_LEFT, MOVE_UP_RIGHT, MOVE_RIGHT, MOVE_LEFT]
        if dir == MOVE_DOWN:
            return (
                [MOVE_DOWN_LEFT, MOVE_DOWN_RIGHT]
                if not panic
                else [MOVE_DOWN_LEFT, MOVE_DOWN_RIGHT, MOVE_RIGHT, MOVE_LEFT]
            )
        if dir == MOVE_LEFT:
            return [MOVE_UP_LEFT, MOVE_DOWN_LEFT] if not panic else [MOVE_UP_LEFT, MOVE_UP_RIGHT, MOVE_UP, MOVE_DOWN]
        if dir == MOVE_RIGHT:
            return (
                [MOVE_UP_RIGHT, MOVE_DOWN_RIGHT] if not panic else [MOVE_UP_RIGHT, MOVE_DOWN_RIGHT, MOVE_UP, MOVE_DOWN]
            )
        if dir == MOVE_WAIT:
            return []
        if dir == MOVE_UP_LEFT:
            return [MOVE_LEFT, MOVE_UP] if not panic else [MOVE_LEFT, MOVE_UP, MOVE_UP_RIGHT, MOVE_DOWN_LEFT]
        if dir == MOVE_DOWN_LEFT:
            return [MOVE_DOWN, MOVE_LEFT] if not panic else [MOVE_DOWN, MOVE_LEFT, MOVE_UP_LEFT, MOVE_DOWN_RIGHT]
        if dir == MOVE_UP_RIGHT:
            return [MOVE_UP, MOVE_RIGHT] if not panic else [MOVE_UP, MOVE_RIGHT, MOVE_UP_LEFT, MOVE_DOWN_RIGHT]
        if dir == MOVE_DOWN_RIGHT:
            return [MOVE_DOWN, MOVE_RIGHT] if not panic else [MOVE_DOWN, MOVE_RIGHT, MOVE_DOWN_LEFT, MOVE_UP_RIGHT]

    def move_randomly(self):
        list = []

        if d(20) < 10:
            self.actor.move(MOVE_WAIT)

        for item in MOVES:
            list.append(item)

        random.shuffle(list)
        success = False
        while len(list) > 0 and not success:
            dir = list.pop()
            new_pos = get_new_pos(self.actor.pos(), dir)
            act = self.game.get_actor_at(new_pos)
            if act is not None:
                if act not in self.hostile:
                    continue
            success = self.actor.move(dir)

    def stand_still(self):
        self.actor.move(MOVE_WAIT)

    def is_morale_down(self):
        return not self._morale()

    def is_morale_up(self):
        return self._morale()

    def _morale(self):
        total = 0
        current = 0
        for zone in self.actor.HP.zones:
            total += getattr(self.actor.HP, zone)[0]
            current += getattr(self.actor.HP, zone)[0]
        try:
            return int(float(current) / total * 100) > 100 - self.actor.morale
        except ZeroDivisionError as e:
            print(f"Error: {e}\nWhere total = {total} and current = {current}")

    def can_move_away_from_foe(self, foe):
        dir = self.actor.opposite_dir(foe)
        dirs = [dir]
        dirs.extend(self.build_alternate_dirs(dir, True))
        old_pos = self.actor.pos()
        for dir in dirs:
            new_pos = get_new_pos(old_pos, dir)
            result = self.game.is_move_valid(self.actor, new_pos)
            if result:
                return True
        return False

    def can_move_toward_foe(self, foe):
        x1, y1 = self.actor.pos()
        x2, y2 = foe.pos()
        if get_dis(x1, y1, x2, y2) <= 1:
            return False
        dir = self.actor.locateDirection(foe)
        dirs = [dir]
        dirs.extend(self.build_alternate_dirs(dir))
        old_pos = self.actor.pos()
        for dir in dirs:
            new_pos = get_new_pos(old_pos, dir)
            result = self.game.is_move_valid(self.actor, new_pos)
            if result:
                return True
        return False

    def to_close_to_foe(self, foe):
        if self.wanna_use_range():
            x1, y1 = self.actor.pos()
            x2, y2 = foe.pos()
            if get_dis(x1, y1, x2, y2) <= 4:
                return True
        else:
            return False

    def too_far_from_foe(self, foe):
        x1, y1 = self.actor.pos()
        x2, y2 = foe.pos()
        if self.wanna_use_range():
            if get_dis(x1, y1, x2, y2) > 7:
                return True
            return False
        if get_dis(x1, y1, x2, y2) > 1:
            return True
        return False

    def move_away_from_foe(self, foe):
        #        if dir is not None:
        #            self.actor.move(dir)
        #            return
        dir = self.actor.opposite_dir(foe)
        dirs = [dir]
        dirs.extend(self.build_alternate_dirs(dir, True))
        old_pos = self.actor.pos()
        for dir in dirs:
            new_pos = get_new_pos(old_pos, dir)
            result = self.game.is_move_valid(self.actor, new_pos)
            if result:
                self.actor.move(d)
                return
        self.stand_still()

    def move_toward_foe(self, foe):
        #        if dir is not None:
        #            self.actor.move(dir)
        #            return
        dir = self.actor.locateDirection(foe)
        dirs = [dir]
        dirs.extend(self.build_alternate_dirs(dir))
        old_pos = self.actor.pos()
        for dir in dirs:
            new_pos = get_new_pos(old_pos, dir)
            result = self.game.is_move_valid(self.actor, new_pos)
            if result:
                self.actor.move(d)
                return
        self.stand_still()

    def can_attack_foe(self, foe):
        return True

    def wanna_use_range(self):
        if self.actor.ready_to_range():
            return True
        else:
            return False

    def attack_foe(self, foe):
        x1, y1 = self.actor.pos()
        x2, y2 = foe.pos()
        if self.wanna_use_range() and get_dis(x1, y1, x2, y2) > 1.5:
            if not self.actor.range_equipped():
                self.actor.equip_range()
                return
            else:
                self.actor.fire(foe.pos())
                return
        else:
            if not self.actor.melee_equipped():
                self.actor.equip_melee()
                return
            dir = self.actor.locateDirection(foe)
            self.actor.move(dir)
            return
        self.stand_still()
        print("ouch")


class SmarterAI(AI):
    def __init__(self, actor):
        AI.__init__(self, actor)
        self.hostile.add(self.game.player.id)

    def act(self):

        foes = self.get_all_foes_in_sight()
        foes.sort(
            cmp=lambda x, y: int(get_dis(x.pos(), self.actor.pos()) * 100)
            - int(get_dis(y.pos(), self.actor.pos()) * 100)
        )

        # if not self.seeing_player():
        #    self.stand_still()
        #    return

        # foe = self.game.player
        if len(foes) > 0:

            foe = foes[0]

            if (self.is_morale_down() or self.to_close_to_foe(foe)) and self.can_move_away_from_foe(foe):
                self.move_away_from_foe(foe)
            elif (self.is_morale_up() and self.too_far_from_foe(foe)) and self.can_move_toward_foe(foe):
                self.move_toward_foe(foe)
            elif self.can_attack_foe(foe):
                self.attack_foe(foe)
            else:
                self.stand_still()
        else:
            if len(self.friends) > 0:
                self.move_toward_foe(self.game.get_actor_by_id(self.friends[0]))
            else:
                self.stand_still()


class SimpleAI(AI):
    def __init__(self, actor: Actor):
        AI.__init__(self, actor)

    def act(self):
        self.move_randomly()


class HenchmanAI(AI):
    def __init__(self, actor):
        AI.__init__(self, actor)
        # self.friends.append(self.game.player.id)

    def act(self):

        foes = self.get_all_foes_in_sight()
        foes.sort(
            cmp=lambda x, y: int(get_dis(x.pos(), self.actor.pos()) * 100)
            - int(get_dis(y.pos(), self.actor.pos()) * 100)
        )

        if len(foes) > 0:

            foe = foes[0]
            # Debug.debug('henchman: %s' % (foe))

            if (self.is_morale_down() or self.to_close_to_foe(foe)) and self.can_move_away_from_foe(foe):
                self.move_away_from_foe(foe)
            elif (self.is_morale_up() and self.too_far_from_foe(foe)) and self.can_move_toward_foe(foe):
                self.move_toward_foe(foe)
            elif self.can_attack_foe(foe):
                self.attack_foe(foe)
            else:
                self.stand_still()
        else:
            if len(self.friends) > 0:
                self.move_toward_foe(self.game.get_actor_by_id(list(self.friends)[0]))
            else:
                self.stand_still()

        if self.actor.timer == 0:
            print("ouch")
            self.stand_still()


class Humanoid(Actor):

    tiles = None

    def __init__(self, add):
        Actor.__init__(self, add)
        self.t = None
        self.check_tiles()
        self.img_body = 1, 0
        self.name = "Player"

    def check_tiles(self):
        if Humanoid.tiles is None:
            Humanoid.tiles = Res("dc-pl.png", TILESIZE)

    def get_tile(self):
        self.check_tiles()
        return Actor.get_tile(self)

    def clear_surfaces(self):
        Actor.clear_surfaces(self)
        for item in self.items:
            item.clear_surfaces()
        self.cur_surf = None
        Humanoid.tiles = None


class Human(Humanoid):
    """"""

    desc = "was versatile and talented at every topic."

    def __init__(self, add, gender=0):
        Humanoid.__init__(self, add)
        self.img_body = 0 + gender, 0
        self.MOVE = 4


class Alb(Humanoid):
    """"""

    desc = "was a quick and wiry person."

    def __init__(self, add, gender=0):
        Humanoid.__init__(self, add)
        self.img_body = 10 + gender, 0
        self.MOVE = 5


class Naga(Humanoid):
    """"""

    desc = "was less talented in melee-weapons, but gifted in magic."

    def __init__(self, add, gender=0):
        Humanoid.__init__(self, add)
        spell = random.choice([FrostRay, HeatRay, LesserHealing, Regeneration, Identify])
        self.spells.append(spell())
        self.MOVE = 3
        del self.slot.__dict__["trousers"]
        del self.slot.slots["trousers"]
        del self.slot.__dict__["boots"]
        del self.slot.slots["boots"]


class Class(object):
    """"""

    def __init__(self, host):
        self.host = host


class Fighter(Class):
    """"""

    desc = "Thanks to unremittingly training, $$$ was skilled at all weapons."

    def __init__(self, host):
        Class.__init__(self, host)
        i = Populator.create_item("Flail", "basic_weapons", 2)
        self.host.pick_up(i)
        self.host.equip(i)

        c = Populator.create_item("ChainmailShirt", "basic_armor", 2)
        self.host.pick_up(c)
        self.host.equip(c)

        b = Populator.create_item("Bow", "basic_weapons", 0)
        self.host.pick_up(b)

        for _ in range(0, 3):
            r = Populator.create_item("Arrows", "basic_weapons", 0)
            self.host.pick_up(r)

        for _ in range(0, 3):
            r = Populator.create_item("Darts", "basic_weapons", 0)
            self.host.pick_up(r)

        # if hasattr(self.host.slot,'trousers'):
        #    t = Populator.create_item('Trousers', 'basic_stuff', 2)
        #    self.host.pick_up(t)
        #    self.host.equip(t)
        self.host.timer = 0


class Barbarian(Class):
    """"""

    desc = "Since his youth, $$$ clearly loved one weapon the most: the Axe."

    def __init__(self, host):
        Class.__init__(self, host)
        i = Populator.create_item("Axe", "basic_weapons", 25)
        self.host.pick_up(i)
        self.host.equip(i)

        if hasattr(self.host.slot, "trousers"):
            t = Populator.create_item("Trousers", "basic_stuff", 2)
            self.host.pick_up(t)
            self.host.equip(t)
        self.host.timer = 0


class Priest(Class):
    """"""

    desc = "Since %%% birth, $$$ stood up for Law and Order."

    def __init__(self, host):
        Class.__init__(self, host)
        self.host.timer = 0


class Sorcerer(Class):
    """"""

    desc = "All %%% live $$$ tried to master the Elemental-Forces "

    def __init__(self, host):
        Class.__init__(self, host)
        self.host.spells.append(FireBall())
        self.host.timer = 0


class Necromancer(Class):
    """"""

    desc = "Allured by the Power of Chaos, $$$ was a fearsome Wizrad."

    def __init__(self, host):
        Class.__init__(self, host)
        self.host.spells.append(CorpseDance())
        self.host.spells.append(DrainLife())
        self.host.timer = 0


class Skills(object):
    def __init__(self, host):

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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        for item in state:
            self.__dict__[item] = state[item]

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        self.__dict__[attr] = value


class HitZones(object):
    def __init__(self, host):

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

    def get_random_zone(self):
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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        for item in state:
            self.__dict__[item] = state[item]

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        self.__dict__[attr] = value


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
                                    item.read = ReadGenericBook
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
            r1 = Room(0, 0, w, h)
            split(r1, s)
            while array is None and i < 20:
                i += 1
                try:
                    array = create(r1)
                except Exception:
                    array = None
                    r1 = Room(0, 0, w, h)
                    split(r1, s)

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


class Effect(object):
    notrigger = [IF_RANGED]

    def __init__(self, duration, host, owner):
        self.duration = duration
        self.host = host
        self.owner = owner
        host.running_fx.append(self)

    def tick(self):
        self.duration -= 1
        if self.duration <= 0:
            if self in self.host.running_fx:
                self.host.running_fx.remove(self)


class StunEffect(Effect):
    def __init__(self, host, owner):
        dur = d(3)
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Stuns the enemy"

    def tick(self):
        self.host.timer += self.host.speed * d(3)
        if self.host == self.host.game.player:
            self.host.game.shout("You are stunned")
        else:
            self.host.game.shout("%s is stunned" % (self.host.name))

        Effect.tick(self)


class BleedEffect(Effect):
    def __init__(self, host, owner):
        dur = d(10)
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Makes the enemy bleed"

    def tick(self):
        self.host.game.do_damage(self.host, d(3), D_GENERIC, self.owner)
        if self.host == self.host.game.player:
            self.host.game.shout("You are bleeding")
        else:
            self.host.game.shout("%s bleeds" % (self.host.name))
        Effect.tick(self)


class BugPoisonEffect(Effect):
    def __init__(self, host, owner):
        dur = d(25)
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Poisons the enemy"

    def tick(self):
        if d(100) < 5:
            self.host.timer += self.host.speed * d(5)
            if self.host == self.host.game.player:
                self.host.game.shout("You suddenly fell asleep")
            else:
                self.host.game.shout("%s suddenly fells asleep" % (self.host.name))
        Effect.tick(self)


class YumuraPoisonEffect(Effect):
    def __init__(self, host, owner):
        dur = d(10)
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Poisons the enemy"

    def tick(self):
        self.host.game.do_damage(self.host, d(3), D_POISON, self.owner)
        notice = False
        if d(100) < 10:
            StunEffect(self.host, self.owner)
            notice = True
        if d(100) < 10:
            DazzleEffect(self.host, self.owner)
            notice = True
        if d(100) < 10:
            self.host.game.do_damage(self.host, d(3), D_POISON, self.owner)
            notice = True
        if d(100) < 2:
            self.host.game.do_damage(self.host, d(25), D_POISON, self.owner)
            notice = True
        if notice:
            if self.host == self.host.game.player:
                self.host.game.shout("You are poisoned")
            else:
                self.host.game.shout("%s is poisoned" % (self.host.name))
        Effect.tick(self)


class KillerbeePoisonEffect(Effect):
    def __init__(self, host, owner):
        dur = d(10)
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Poisons the enemy"

    def tick(self):
        self.host.game.do_damage(self.host, d(3), D_POISON, self.owner)
        if d(100) < 35:
            StunEffect(self.host, self.owner)
        if d(100) < 35:
            DazzleEffect(self.host, self.owner)
        if self.host == self.host.game.player:
            self.host.game.shout("You are poisoned")
        else:
            self.host.game.shout("%s is poisoned" % (self.host.name))
        Effect.tick(self)


class StrokingEffect(Effect):
    def __init__(self, host, owner):
        dur = 1
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Strokes the enemy"

    def tick(self):
        if self.host == self.host.game.player:
            self.host.game.shout("You are getting stroked by %s" % (self.owner.name))
        else:
            self.host.game.shout("%s is getting stroked" % (self.host.name))
        Effect.tick(self)


class FloatingEyeGazeEffect(Effect):
    def __init__(self, host, owner):
        dur = d(10)
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Stuns the enemy"

    def tick(self):
        self.host.timer += 1000
        if self.host == self.host.game.player:
            self.host.game.shout("You are stunned by the Floating Eye`s gaze!")
        else:
            self.host.game.shout("%s is stunned by the Floating Eye`s gaze!" % (self.host.name))

        Effect.tick(self)


class AcidSplatterEffect(Effect):
    notrigger = []

    def __init__(self, host, owner):
        dur = 1
        Effect.__init__(self, dur, host, owner)
        actors = owner.game.get_all_srd_actors(owner.pos())
        for act in actors:
            Effect.__init__(self, dur, act, owner)
        # weaponinfotext = "Splatters the enemy"

    def tick(self):
        self.host.game.do_damage(self.host, d(3), D_ACID, self.owner)
        if self.host == self.host.game.player:
            self.host.game.shout("You are splashed by acid!")
        else:
            self.host.game.shout("%s is splashed by acid!" % (self.host.name))
        Effect.tick(self)


class FrostEffect(Effect):
    def __init__(self, host, owner):
        dur = 1
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Freezes the enemy"

    def tick(self):
        self.host.game.do_damage(self.host, d(3), D_COLD, self.owner)
        if self.host == self.host.game.player:
            self.host.game.shout("You are freezing!")
        else:
            self.host.game.shout("%s is freezing!" % (self.host.name))
        Effect.tick(self)


class HeatEffect(Effect):
    def __init__(self, host, owner):
        dur = 1
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Burns the enemy"

    def tick(self):
        self.host.game.do_damage(self.host, d(3), D_FIRE, self.owner)
        if self.host == self.host.game.player:
            self.host.game.shout("You are getting burned!")
        else:
            self.host.game.shout("%s is getting burned!" % (self.host.name))
        Effect.tick(self)


class SplitEffect(Effect):
    notrigger = []

    def __init__(self, host, owner):
        dur = 1
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "You should not read this"

    def tick(self):
        new_pos = self.host.game.get_free_adj(self.owner.pos())
        if new_pos is not None:
            self.owner.game.shout("%s splits in half!" % (self.owner.name))
            new = Populator.create_creature(self.owner.pop_name, self.owner.filename)
            new.set_pos(new_pos)
            new.game.add_actor(new)
            self.owner.health = self.owner.health / 2 + 1
            self.owner.cur_health = self.owner.cur_health / 2 + 1
            new.health = self.owner.health
            new.cur_health = self.owner.cur_health
            new.xp_value = self.owner.xp_value / 3 + 2
        Effect.tick(self)


class DazzleEffect(Effect):
    def __init__(self, host, owner):
        dur = d(4)
        Effect.__init__(self, dur, host, owner)
        # weaponinfotext = "Blinds the enemy"

    def tick(self):
        self.host.dazzled = True
        if self.host == self.host.game.player:
            self.host.game.shout("You are blinded!")
        else:
            self.host.game.shout("%s is blinded!" % (self.host.name))
        Effect.tick(self)


class RegenerationEffect(Effect):
    def __init__(self, host, owner):
        dur = 10
        Effect.__init__(self, dur, host, owner)

    def tick(self):
        a = -d(4)
        if self.host.cur_health - a > self.host.health:
            a = self.host.cur_health - self.host.health
        self.host.game.do_damage(self.host, a, D_ORDER)
        if self.host == self.host.game.player:
            self.host.game.shout("You are regenerating")
        else:
            self.host.game.shout("%s is regenerating" % (self.host.name))
        Effect.tick(self)


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


class Item(object):

    eq_tiles = None
    dd_tiles = None

    game = None

    def __init__(self, add):
        self.game.add_item(self, add)
        self.cur_surf = None
        self.eq_img = None
        self.eq_img_c = None
        self.dd_img = None
        self.dd_img_c = None
        self.blit_pos = None
        self.equipped = False
        self.picked_up = False
        self.y = 0
        self.x = 0
        self.name = "empty"
        self.full_name = "empty"
        self.flags = IF_MELEE | IF_FIRES_DART | IF_RANGED
        self.type = I_VOID
        self.av_fx = []
        self.dv_fx = []
        self.special = False
        self.amount = 0
        self.damage_type = D_GENERIC
        self.infotext = ""
        self.text = ""
        self.player_symbol = None
        self.skills = []
        self.locations = 0
        self.AP = 0
        self.HP = 0
        self.TSP = 0
        self.ENC = 0
        self.H2 = False

    def get_ps(self):
        if self.player_symbol is None:
            self.player_symbol = self.game.get_symbol()
        return self.player_symbol

    def used(self):
        self.amount -= 1
        if self.amount == 0:
            return False
        return True

    def get_name(self):
        if self.flags & IF_IDENTIFIED:
            name = self.full_name
        else:
            name = self.name

        if self.amount > 0:
            name += " (%s)" % (self.amount)

        return name

    def read(self, item, obj):
        self.game.shout("Nothing interesting")

    def drink(self, item, obj):
        self.game.shout("Tastes like water")

    def info(self):
        lines = []

        if not self.flags & IF_IDENTIFIED:
            if len(self.infotext) > 0:
                lines.append(self.infotext)
            lines.append("not identified")
            return lines

        if len(self.infotext) > 0:
            lines.append(self.infotext)

        if self.AP > 0 and self.HP > 0:
            lines.append("AP/HP: %i/%i" % (self.AP, self.HP))
        elif self.AP > 0:
            lines.append("AP: %i" % (self.AP))

        lines.append("ENC: %i" % (self.ENC))

        # if self.av > 0:
        #    l.append('av: %i' % (self.av))
        # if self.max_damage > 0:
        #    l.append('dam: %i-%i' % (self.min_damage, self.max_damage))
        # if self.dv > 0:
        #    l.append('dv: %i' % (self.dv))

        # if self.amount > 0:
        #    l.append('count: %i' % (self.amount))

        for fx in self.av_fx:
            lines.append(fx.weaponinfotext)

        for fx in self.dv_fx:
            lines.append(fx.weaponinfotext)

        return lines

    def set_pos(self, pos):
        self.game.update_item_pos(self, pos)
        self.x = pos[0]
        self.y = pos[1]

    def pos(self):
        return self.x, self.y

    def clear_surfaces(self):
        self.eq_img_c = None
        self.dd_img_c = None
        Item.dd_tiles = None
        Item.eq_tiles = None
        self.cur_surf = None
        self = None

    def check_tiles(self):
        if Item.eq_tiles is None:
            Item.eq_tiles = Res("dc-pl.png", TILESIZE)

        if Item.dd_tiles is None:
            Item.dd_tiles = Res("dc-item.png", TILESIZE)

    def get_eq_img(self):
        self.check_tiles()

        if self.eq_img_c is None:
            if self.eq_img is None:
                self.eq_img_c = pygame.Surface((1, 1), pygame.SRCALPHA, 32)
            else:
                self.eq_img_c = self.eq_tiles.get_subs(self.eq_img)
        return self.eq_img_c

    def get_dd_img(self):
        self.check_tiles()

        if self.dd_img_c is None:
            if self.dd_img is None:
                self.dd_img_c = pygame.Surface((1, 1), pygame.SRCALPHA, 32)
            else:
                self.dd_img_c = self.dd_tiles.get(self.dd_img)
        return self.dd_img_c


class Corpse(Item):
    def __init__(self, owner):
        Item.__init__(self, True)
        self.type = I_CORPSE
        self.dd_img = 208
        self.flags = IF_EATABLE
        self.name = "%s corpse" % (owner.name)
        self.full_name = self.name
        self.set_pos(owner.pos())
        if not self.flags & IF_IDENTIFIED:
            self.flags ^= IF_IDENTIFIED


class Armor(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_ARMOR


class Cloak(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_ARMOR


class Weapon(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_WEAPON


class Unarmed(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_WEAPON
        self.skills.append(WT_UNARMED)
        self.damage = "1D3", lambda: cd(int(1), int(3))
        # item.damage = value, lambda : cd(int(no), int(ey)) + int(add)


class Shield(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_SHIELD


class Boots(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_BOOTS


class Helmet(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_HELMET


class Trousers(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_TROUSERS


class Ammo(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_AMMO


class Gold(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_GOLD


class Stuff(Item):
    def __init__(self, add):
        Item.__init__(self, add)
        self.type = I_STUFF


class Spell(object):

    game = None

    def __init__(self):
        self.phys_cost = 10
        self.mind_cost = 25
        self.name = "generic"
        self.infotext = "nothing"
        self.color = WHITE
        self.type = ST_GENERIC

    def get_ray_target(self, cpos, tpos):
        if cpos != tpos:
            poss = line(cpos[0], cpos[1], tpos[0], tpos[1])
            poss.pop(0)
            for pos in poss:
                actor = self.game.get_actor_at(pos)
                if actor is not None:
                    return actor
        else:
            return self.caster
        return None

    def cast(self, caster):
        self.caster = caster
        self.game.wait_for_target(self.target_choosen)

    def info(self):
        lines = ["PHY: %i MND: %i" % (self.phys_cost, self.mind_cost)]
        if isinstance(self.infotext, str):
            lines.append(self.infotext)
        else:
            for i in self.infotext:
                lines.append(i)
        return lines


class ChaosSpell(Spell):
    def __init__(self):
        Spell.__init__(self)
        self.color = PURPLE
        self.type = ST_GENERIC


class FoulnessRay(ChaosSpell):
    def __init__(self):
        ChaosSpell.__init__(self)
        self.phys_cost = 5
        self.mind_cost = 5
        self.name = "Ray of Foulness"
        self.infotext = "Damage Foes with Chaos"

    def target_choosen(self, pos):
        target = self.get_ray_target(self.caster.pos(), pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            fx = RayFX(BLACK, GREEN, self.caster.pos(), target.pos())
            self.game.drawGFX(fx)
            amount = d(self.caster.mind / 20) + self.caster.mind / 20
            self.game.do_damage(self.caster, amount / 2, D_CHAOS)
            self.game.do_damage(target, amount, D_CHAOS, self.caster)
            self.game.shout("%s befouled %s" % (self.caster.name, target.name))


class CorpseDance(ChaosSpell):
    def __init__(self):
        ChaosSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 45
        self.name = "Corpse Dance"
        self.infotext = "Reanimates corpse"

    def target_choosen(self, pos):
        targets = self.game.get_items_at(pos)
        random.shuffle(targets)
        for item in targets:
            if item.type == I_CORPSE:
                self.game.del_item(item)
                self.game.summon_monster(self.caster, "Skeleton", "easy_other", item.pos())
                return


class DrainLife(ChaosSpell):
    def __init__(self):
        ChaosSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 45
        self.name = "Drain Life"
        self.infotext = "Damage Foes, heals self"

    def target_choosen(self, pos):
        target = self.get_ray_target(self.caster.pos(), pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            fx = RayFX(BLACK, GREEN, self.caster.pos(), target.pos())
            self.game.drawGFX(fx)
            amount = d(self.caster.mind / 20) + self.caster.mind / 20
            self.game.do_damage(self.caster, -amount / 2, D_CHAOS)
            self.game.do_damage(target, amount, D_CHAOS, self.caster)
            self.game.shout("%s drained %s" % (self.caster.name, target.name))


class ColdSpell(Spell):
    def __init__(self):
        Spell.__init__(self)
        self.color = BLUE
        self.type = ST_GENERIC


class FrostRay(ColdSpell):
    def __init__(self):
        ColdSpell.__init__(self)
        self.phys_cost = 5
        self.mind_cost = 30
        self.name = "Frost Ray"
        self.infotext = "Damage Foes with cold"

    def target_choosen(self, pos):
        target = self.get_ray_target(self.caster.pos(), pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            fx = RayFX(WHITE, BLUE, self.caster.pos(), target.pos())
            self.game.drawGFX(fx)
            amount = d(self.caster.mind / 20) + self.caster.mind / 10 + 2
            self.game.do_damage(target, amount, D_COLD, self.caster)
            self.game.shout("%s freezed %s" % (self.caster.name, target.name))


class FireSpell(Spell):
    def __init__(self):
        Spell.__init__(self)
        self.color = RED
        self.type = ST_GENERIC


class FireBall(FireSpell):
    def __init__(self):
        FireSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 35
        self.name = "Fireball"
        self.infotext = "Causes a ball of Fire to explode"

    def target_choosen(self, pos):

        radius = 1 + (self.caster.mind - 100) / 50
        fx = BallFX(RED, YELLOW, self.caster.pos(), pos, radius)
        self.game.drawGFX(fx)
        actors = self.caster.game.get_all_srd_actors(pos, radius, True)
        for act in actors:
            amount = d(self.caster.mind / 20) + self.caster.mind / 20 + 2
            self.game.do_damage(act, amount, D_FIRE, self.caster)
            self.game.shout("%s burns %s" % (self.caster.name, act.name))


class HeatRay(FireSpell):
    def __init__(self):
        FireSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 30
        self.name = "Heat Ray"
        self.infotext = "Damage Foes with Fire"

    def target_choosen(self, pos):
        target = self.get_ray_target(self.caster.pos(), pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            fx = RayFX(RED, YELLOW, self.caster.pos(), target.pos())
            self.game.drawGFX(fx)
            amount = d(self.caster.mind / 20) + self.caster.mind / 10 + 3
            self.game.do_damage(target, amount, D_FIRE, self.caster)
            self.game.shout("%s burns %s" % (self.caster.name, target.name))


#        target = self.get_ray_target(self.caster.pos(), pos)
#        if target is None:
#            self.game.shout('Your spell fizzles')
#        else:
#            fx = RayFX(WHITE,BLUE,self.caster.pos(),target.pos())
#            self.game.drawGFX(fx)
#            amount = d(self.caster.mind / 20) + self.caster.mind / 20
#            self.game.do_damage(target, amount, D_COLD,self.caster)
#            self.game.shout('%s freezed %s' % (self.caster.name, target.name))


class GenericSpell(Spell):
    def __init__(self):
        Spell.__init__(self)
        self.color = GREEN
        self.type = ST_GENERIC


class LesserHaste(GenericSpell):
    def __init__(self):
        GenericSpell.__init__(self)
        self.phys_cost = 5
        self.mind_cost = 15
        self.name = "Lesser Haste"
        self.infotext = "Speed Up"

    def target_choosen(self, pos):
        target = self.game.get_actor_at(pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            amount = d(self.caster.mind / 10) + 3
            if target.cur_speed > target.speed / 2:
                target.cur_speed -= amount
            self.game.shout("%s speeds up %s" % (self.caster.name, target.name))


class Identify(GenericSpell):
    def __init__(self):
        GenericSpell.__init__(self)
        self.phys_cost = 0
        self.mind_cost = 25
        self.name = "Identify"
        self.infotext = "Identify an Item"

    def cast(self, caster):
        self.caster = caster
        self.game.do_identify()


class OrderSpell(Spell):
    def __init__(self):
        Spell.__init__(self)
        self.color = WHITE
        self.type = ST_ORDER


class Regeneration(OrderSpell):
    def __init__(self):
        OrderSpell.__init__(self)
        self.phys_cost = 25
        self.mind_cost = 65
        self.name = "Regeneraton"
        self.infotext = "Target regenerates"

    def target_choosen(self, pos):
        target = self.game.get_actor_at(pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            self.game.shout("%s regenerate %s" % (self.caster.name, target.name))
            r = RegenerationEffect(target, self.caster)
            r.tick()


class LesserHealing(OrderSpell):
    def __init__(self):
        OrderSpell.__init__(self)
        self.phys_cost = 5
        self.mind_cost = 25
        self.name = "Lesser Healing"
        self.infotext = "Cures small wounds"

    def target_choosen(self, pos):
        target = self.game.get_actor_at(pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            amount = d(self.caster.mind / 10) + 3
            if target.cur_health + amount > target.health:
                amount = target.health - target.cur_health
            self.game.do_damage(target, -amount)
            self.game.shout("%s healed %s" % (self.caster.name, target.name))


class Healing(OrderSpell):
    def __init__(self):
        OrderSpell.__init__(self)
        self.phys_cost = 10
        self.mind_cost = 55
        self.name = "Healing"
        self.infotext = "Cures wounds"

    def target_choosen(self, pos):
        target = self.game.get_actor_at(pos)
        if target is None:
            self.game.shout("Your spell fizzles")
        else:
            amount = d(self.caster.mind / 10) + d(self.caster.mind / 10) + 5
            self.game.do_damage(target, -amount)
            self.game.shout("%s healed %s" % (self.caster.name, target.name))


def leg(tot):
    tot += 4
    return tot / 5


def head(tot):
    tot += 4
    return tot / 5


def arm(tot):
    tot += 4
    v = tot / 5 - 1
    return max(v, 1)


def chest(tot):
    tot += 4
    return tot / 5 + 2


def abdomen(tot):
    tot += 4
    return tot / 5 + 1


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


def LesserProtection(item):
    item.full_name += " of lesser Protection"
    item.dv += random.randint(5, 25)


def BookOfTOVU(item):
    pass


def BookOfRegeneration(item):
    item.full_name += " of Regeneration"
    item.spell = Regeneration


def BookOfIdentify(item):
    item.full_name += " of Identify"
    item.spell = Identify


def BookOfLesserHealing(item):
    item.full_name += " of Lesser Healing"
    item.spell = LesserHealing


def BookOfHealing(item):
    item.full_name += " of Healing"
    item.spell = Healing


def BookOfFoulnessRay(item):
    item.full_name += " of Foulness-Ray"
    item.spell = FoulnessRay


def BookOfFrostRay(item):
    item.full_name += " of Frost-Ray"
    item.spell = FrostRay


def BookOfLesserHaste(item):
    item.full_name += " of Lesser Haste"
    item.spell = LesserHaste


def ReadBookOfTOVU(self, actor):
    actor.game.shout("Your read the Book of Vile Umbrages")


def ReadGenericBook(self, actor):
    learn_spell(self, actor)


def learn_spell(book, actor):
    if not book.flags & IF_IDENTIFIED:
        book.flags ^= IF_IDENTIFIED
    s = book.spell()
    actor.timer += actor.cur_speed * 3
    for spell in actor.spells:
        if isinstance(spell, book.spell):
            actor.game.shout("You already know the %s-Spell" % (s.name))
            return
    actor.spells.append(s)
    actor.game.shout("You learned the %s-Spell" % (s.name))


def PotionOfKillbeePoison(item):
    item.full_name += " of Killerbee-Poison"
    item.weaponinfotext = "Dangerous Poison"


def DrinkPotionOfKillbeePoison(self, actor):
    KillerbeePoisonEffect(actor, None)


def PotionOfYumuraPoison(item):
    item.full_name += " of Yumura-Poison"


def DrinkPotionOfYumuraPoison(self, actor):
    YumuraPoisonEffect(actor, None)


def PotionOfRegeneration(item):
    item.full_name += " of Killerbee-Poison"


def DrinkPotionOfRegeneration(self, actor):
    RegenerationEffect(actor, None)


def PotionOfEndurance(item):
    item.full_name += " of Endurance"


def DrinkPotionOfEndurance(self, actor):
    actor.cur_endurance += d(10) + d(10)


def PotionOfMind(item):
    item.full_name += " of Mind"


def DrinkPotionOfMind(self, actor):
    actor.cur_mind += d(10) + d(10)


def PotionOfSpellcaster(item):
    item.full_name += " of Spellcasters"


def DrinkPotionOfSpellcaster(self, actor):
    actor.cur_endurance += d(10) + d(10)
    actor.cur_mind += d(10) + d(10)


def PotionOfHealing(item):
    item.full_name += " of Healing"


def DrinkPotionOfHealing(self, actor):
    actor.cur_health += d(10)


races = (("Human", 0, 1, Human), ("Naga", 16, 17, Naga), ("Alb", 10, 11, Alb))

classkits = (
    ("Fighter", Fighter),
    ("Barbarian", Barbarian),
    ("Sorcerer", Sorcerer),
    ("Priest", Priest),
    ("Necromancer", Necromancer),
)


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


if __name__ == "__main__":
    r1 = Room(0, 0, 100, 50)
    split(r1, 5)
    map_array = create(r1)
    for line in map_array:
        item = ""
        for s in line:
            item = item + str(s)
        print(item)
