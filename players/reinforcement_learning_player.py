"""A Reinforcement Learning player

Most Basic Players only play if they know for certain that a card is
playable.  Otherwise, if there are hints available and another player
has a playable card, Basic will give a random hint about that card.
Otherwise, they discard randomly.
Basic players can only handle rainbow as an ordinary 6th suit.
"""

import random
from hanabi_classes import AIPlayer
from pprint import pprint

class ReinforcementLearningPlayer(AIPlayer):

    @classmethod
    def get_name(cls):
        return 'rl'


    def get_observation(self, r):
        '''This is a subset of the round information that would be available to a player'''
        
        observation = {}
        me = r.whoseTurn
        observed_hands = []
        for hand in r.h[me+1:r.nPlayers]:
            pprint(hand.cards)
            {
                hand.cards.
            }
            observed_hands.append(hand.cards)

        observation['player_hands'] = observed_hands
        observation['whoseTurn'] = r.whoseTurn
        observation['progress'] = r.progress
        observation['hints'] = r.hints
        observation['lighting'] = r.lighting
        observation['discardpile'] = r.discardpile
        observation['suits'] = r.suits
        observation['deck_size'] = len(r.deck)
        
        return NotImplementedError


    def get_legal_actions(self, observation):
        '''Returns a list of the legal game actions'''
        return NotImplementedError
    

    def select_action(self, observation, possible_actions):
        '''Looks at the world and selects an action based on the policy'''
        return NotImplementedError


    def play(self, r):

        observation = self.get_observation(r)
        possible_actions = self.get_legal_actions(observation)
        action = self.select_action(observation, [possible_actions])
        
        
        cards = r.h[r.whoseTurn].cards
        return 'discard', random.choice(cards)


        # cards = r.h[r.whoseTurn].cards
        # progress = r.progress
        # playableCards = get_plays(cards, progress)

        # if playableCards == []:
        #     return 'discard', random.choice(cards)
        # else:
        #     return 'play', random.choice(playableCards)


    def end_game_logging(self):
        """Can be overridden to perform logging at the end of the game"""
        pass
