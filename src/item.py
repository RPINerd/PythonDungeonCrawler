import random

import pygame

from effects.av_effects import KillerbeePoisonEffect, YumuraPoisonEffect
from effects.generic_effects import RegenerationEffect
from magic.chaos_spells import FoulnessRay
from magic.cold_spells import FrostRay
from magic.generic_spells import Identify, LesserHaste
from magic.order_spells import Healing, LesserHealing, Regeneration
from pdcglobal import (
    D_GENERIC,
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
    IF_EATABLE,
    IF_FIRES_DART,
    IF_IDENTIFIED,
    IF_MELEE,
    IF_RANGED,
    TILESIZE,
    WT_UNARMED,
    cd,
    d,
)
from pdcresource import Res


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
