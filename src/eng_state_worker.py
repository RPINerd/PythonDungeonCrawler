from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from key_mapping import TARGET_KEY
from pdcglobal import IF_IDENTIFIED, S_GFX, S_RUN, d

if TYPE_CHECKING:
    from engine import Engine


class StateWorker:

    """Handles game state transitions and input processing for different states."""

    def __init__(self, game: Engine) -> None:
        self.game: Engine = game

    def stats(self, key: int) -> None:
        """Handle stat improvement selection."""
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            stat = self.game._items_to_choose[pygame.key.name(key)]
            if self.game.player.xp < stat.cost:
                self.game.shout("You don`t have enough XP to improve %s" % (stat.name))
            else:
                self.game.player.xp -= stat.cost
                cur = getattr(self.game.player, stat.name.lower())
                setattr(self.game.player, stat.name.lower(), cur + 2 + d(5))
                stat.cost += stat.cost / 10 + 5
                self.game.shout("You improved %s" % (stat.name))

            self.game.state = S_RUN
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN

    def cursor(self, key: int) -> None:
        """Handle cursor mode input."""
        if key == pygame.K_ESCAPE:
            self.game.state = S_RUN
        if key == TARGET_KEY:
            if self.game.wait_for_target is not None:
                self.game.target_choosen(self.game.cursor.pos())
                if self.game.state != S_GFX:
                    self.game.state = S_RUN

    def take_off(self, key: int) -> None:
        """Handle item removal."""
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            item = self.game._items_to_choose[pygame.key.name(key)]
            self.game.player.take_off(item)
            self.game.shout("You took off %s" % (item.get_name()))
            self.game.state = S_RUN
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN

    def identify(self, key: int) -> None:
        """Handle item identification."""
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            item = self.game._items_to_choose[pygame.key.name(key)]
            item.flags |= IF_IDENTIFIED
            self.game.shout("You identified %s" % (item.get_name()))
            self.game.state = S_RUN
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN

    def read(self, key: int) -> None:
        """Handle item reading."""
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            item = self.game._items_to_choose[pygame.key.name(key)]
            self.game.player.read(item)
            self.game.shout("You read %s" % (item.get_name()))
            self.game.state = S_RUN
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN

    def throw(self, key: int) -> None:
        """Handle item throwing selection."""
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            self.game.item_to_throw = self.game._items_to_choose[pygame.key.name(key)]
            self.game.call_pl_item_throw()
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN

    def drop(self, key: int) -> None:
        """Handle item dropping."""
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            item = self.game._items_to_choose[pygame.key.name(key)]
            self.game.player.drop(item)
            self.game.shout("You dropped %s" % (item.get_name()))
            self.game.state = S_RUN
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN

    def drink(self, key: int) -> None:
        """Handle potion drinking."""
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            item = self.game._items_to_choose[pygame.key.name(key)]
            self.game.player.drink(item)
            self.game.shout("You quaffed a %s" % (item.get_name()))
            self.game.state = S_RUN
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN

    def pickup(self, key: int) -> None:
        """Handle item pickup."""
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            item = self.game._items_to_choose[pygame.key.name(key)]
            self.game.player.pick_up(item)
            # self.game.shout('You picked up a %s' % (item.get_name()))
            self.game.state = S_RUN
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN

    def equip(self, key: int) -> None:
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            item = self.game._items_to_choose[pygame.key.name(key)]
            if self.game.player.equip(item):
                self.game.shout("You equipped %s" % (item.get_name()))
            self.game.state = S_RUN
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN

    def cast(self, key):
        s = self.game.state
        if pygame.key.name(key) in self.game._items_to_choose.keys():
            spell = self.game._items_to_choose[pygame.key.name(key)]
            if self.game.player.cur_endurance > spell.phys_cost:
                if self.game.player.cur_mind > spell.mind_cost:
                    self.game.player.cast(spell)
                    self.game.redraw_map()
                    self.game.shout("You cast %s" % (spell.name))
                else:
                    self.game.shout("You don't have enough mind to cast %s" % (spell.name))
            else:
                self.game.shout("You don't have enough endurance to cast %s" % (spell.name))
            if s == self.game.state:  # allow state change in spells
                self.game.state = S_RUN
        elif key == pygame.K_ESCAPE:
            self.game.state = S_RUN
