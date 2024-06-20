from actor.actor import Actor

from .ai import AI

# from key_mapping import *
# from pdcglobal import *
# from pdcresource import *


class SimpleAI(AI):
    def __init__(self, actor: Actor):
        AI.__init__(self, actor)

    def act(self):
        self.move_randomly()
