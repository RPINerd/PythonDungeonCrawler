"""
Simple AI implementation for basic enemy behavior.

This module provides a simple AI that moves randomly without any
tactical considerations.
"""

from __future__ import annotations

from actor.actor import Actor

from .ai import AI


class SimpleAI(AI):

    """Simple AI that moves randomly."""

    def __init__(self, actor: Actor) -> None:
        """
        Initialize simple AI for an actor.

        Args:
            actor: The actor controlled by this AI.
        """
        AI.__init__(self, actor)

    def act(self) -> None:
        """Execute one AI action - move randomly."""
        self.move_randomly()
