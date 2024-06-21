import dungeon
from pdcglobal import D_ACID, D_COLD, D_FIRE, D_GENERIC, D_ORDER, D_POISON, IF_RANGED, d


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
            new = dungeon.Populator.create_creature(self.owner.pop_name, self.owner.filename)
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
