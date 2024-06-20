from pdcglobal import ST_GENERIC, WHITE, line


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
