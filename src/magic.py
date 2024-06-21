import random

import effects
import gfx
from pdcglobal import (
    BLACK,
    BLUE,
    D_CHAOS,
    D_COLD,
    D_FIRE,
    GREEN,
    I_CORPSE,
    PURPLE,
    RED,
    ST_GENERIC,
    ST_ORDER,
    WHITE,
    YELLOW,
    d,
    line,
)


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
            fx = gfx.RayFX(BLACK, GREEN, self.caster.pos(), target.pos())
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
            fx = gfx.RayFX(BLACK, GREEN, self.caster.pos(), target.pos())
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
            fx = gfx.RayFX(WHITE, BLUE, self.caster.pos(), target.pos())
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
        fx = gfx.BallFX(RED, YELLOW, self.caster.pos(), pos, radius)
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
            fx = gfx.RayFX(RED, YELLOW, self.caster.pos(), target.pos())
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
            r = effects.RegenerationEffect(target, self.caster)
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
