from __future__ import annotations

import random
from typing import TYPE_CHECKING

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
from pdcglobal import d, get_dis, get_new_pos

if TYPE_CHECKING:
    from actor.actor import Actor
    from engine import Engine


class AI:

    """Base AI class for NPC behavior."""

    game: Engine | None = None

    def __init__(self, actor: Actor) -> None:
        self.actor: Actor = actor
        self.hostile: set[int] = set()
        self.friends: set[int] = set()

    def act(self) -> None:
        """Execute AI turn. Override in subclasses."""
        pass

    def get_all_foes_in_sight(self) -> list[Actor]:
        """Get all hostile actors currently visible."""
        all_foes = self.game.get_all_srd_actors(self.actor.pos(), radius=15)
        seeing = []
        self.actor.sc.do_fov(self.actor.x, self.actor.y, 10)
        for act in all_foes:
            x, y = act.pos()
            if self.actor.sc.lit(x, y) and act.id in self.hostile:  # not act.id in self.friends:
                seeing.append(act)
        return seeing

    def seeing_actor(self, target: Actor) -> bool:
        """Check if actor can see the target."""
        dis = get_dis(self.actor.x, self.actor.y, target.x, target.y)
        if dis > 15:
            return False

        self.actor.sc.do_fov(self.actor.x, self.actor.y, 10)
        x, y = target.pos()
        return self.actor.sc.lit(x, y)

    def seeing_player(self) -> bool:
        """Check if actor can see the player."""
        return self.seeing_actor(self.game.player)

    def get_player_direction(self) -> int:
        """Get direction from actor to player."""
        return self.actor.locateDirection(self.game.player)

    def build_alternate_dirs(self, dir: int, panic: bool = False) -> list[int]:
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

    def move_randomly(self) -> None:
        """Move in a random direction."""
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
        return False

    def attack_foe(self, foe):
        x1, y1 = self.actor.pos()
        x2, y2 = foe.pos()
        if self.wanna_use_range() and get_dis(x1, y1, x2, y2) > 1.5:
            if not self.actor.range_equipped():
                self.actor.equip_range()
                return
            self.actor.fire(foe.pos())
            return
        if not self.actor.melee_equipped():
            self.actor.equip_melee()
            return
        dir = self.actor.locateDirection(foe)
        self.actor.move(dir)
        return
        self.stand_still()
        print("ouch")
