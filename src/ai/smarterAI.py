"""
Smarter AI implementation with tactical behavior.

This module provides an enhanced AI that evaluates threats, maintains
morale, and makes tactical decisions about engagement and retreat.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pdcglobal import get_dis

from .ai import AI

if TYPE_CHECKING:
    from actor.actor import Actor


class SmarterAI(AI):

    """Enhanced AI with tactical decision-making capabilities."""

    def __init__(self, actor: Actor) -> None:
        """
        Initialize smarter AI for an actor.

        Args:
            actor: The actor controlled by this AI.
        """
        AI.__init__(self, actor)
        self.hostile.add(self.game.player.id)

    def act(self) -> None:
        """Execute one AI action with tactical considerations."""
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
        elif len(self.friends) > 0:
            self.move_toward_foe(self.game.get_actor_by_id(self.friends[0]))
        else:
            self.stand_still()
