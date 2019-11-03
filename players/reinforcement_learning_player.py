"""A Reinforcement Learning player

Most Basic Players only play if they know for certain that a card is
playable.  Otherwise, if there are hints available and another player
has a playable card, Basic will give a random hint about that card.
Otherwise, they discard randomly.
Basic players can only handle rainbow as an ordinary 6th suit.
"""

from hanabi_classes import *
from bot_utils import get_plays, deduce_plays
from pprint import pprint

class ReinforcementLearningPlayer(AIPlayer):

    @classmethod
    def get_name(cls):
        return 'rl'

    
    def get_observation(self, r):
        return 


    def play(self, r):
        cards = r.h[r.whoseTurn].cards
        progress = r.progress
        playableCards = get_plays(cards, progress)

        if playableCards == []:
            return 'discard', random.choice(cards)
        else:
            return 'play', random.choice(playableCards)


    def end_game_logging(self):
        """Can be overridden to perform logging at the end of the game"""
        pass
