"""
Henchman AI implementation for companion behavior.

This module provides AI for henchmen/companions that follow and support
the player while making tactical combat decisions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pdcglobal import get_dis

from .ai import AI

if TYPE_CHECKING:
    from actor.actor import Actor


class HenchmanAI(AI):

    """AI for henchmen and companion characters."""

    def __init__(self, actor: Actor) -> None:
        """
        Initialize henchman AI for an actor.

        Args:
            actor: The actor controlled by this AI.
        """
        AI.__init__(self, actor)

    def act(self) -> None:
        """Execute one AI action with companion logic."""
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
        elif len(self.friends) > 0:
            self.move_toward_foe(self.game.get_actor_by_id(list(self.friends)[0]))
        else:
            self.stand_still()

        if self.actor.timer == 0:
            print("ouch")
            self.stand_still()
