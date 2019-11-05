"""A Reinforcement Learning player

Most Basic Players only play if they know for certain that a card is
playable.  Otherwise, if there are hints available and another player
has a playable card, Basic will give a random hint about that card.
Otherwise, they discard randomly.
Basic players can only handle rainbow as an ordinary 6th suit.
"""

import random
from copy import deepcopy
from hanabi_classes import AIPlayer

from hanabi_classes import *
from bot_utils import *


from pprint import pprint

class ReinforcementLearningPlayer(AIPlayer):

    @classmethod
    def get_name(cls):
        return 'rl'



    # find the newest card in your hand for which info was relevant
    # as long as you haven't drawn any new cards, this should have the same
    # outcome as get_newest_hinted, but without looking at your cards
    def get_my_newest_hinted(self, cards, info):
        hinted = [card for card in cards if info in card['direct']]
        if hinted:
            return max(hinted, key=lambda card: card['time'])

    # find the newest card in another player's hand which info targets
    def get_newest_hinted(self, cards, info):
        hinted = [card for card in cards if matches(card['name'], info)]
        if hinted:
            return max(hinted, key=lambda card: card['time'])

    # discard the oldest card which isn't a known five.  Unless all are fives.
    def get_discard(self, cards):
      nonFives = [card for card in cards if '5' not in card['direct']]
      return min(nonFives if nonFives else cards,
              key=lambda card: card['time'])





    def get_observed_hands(self, r):
        me = r.whoseTurn
        observed_hands = []
        for hand in r.h[me+1:r.nPlayers] + r.h[0:me]:
            # hands.cards has extra info that we won't use... ideally I would remove the extra fields.
            observed_hands.append(hand.cards)
        return observed_hands


    def get_card_knowledge(self, r):
        knowledge = []
        for hand in r.h:
            cards = []
            for card in hand.cards:
                legal_card_info = {key:card[key] for key in ['direct', 'indirect', 'time']}
                cards.append(legal_card_info)
            new_hand = Round.Hand(hand.seat, hand.name)
            new_hand.cards = cards
            knowledge.append(new_hand)
        return knowledge


    def get_observation(self, r):
        '''This is a subset of the round information that would actually be available to a player'''

        observation = {}
        observation['teammate_hands'] = self.get_observed_hands(r)      
        observation['card_knowledge'] = self.get_card_knowledge(r)
        observation['whoseTurn'] = r.whoseTurn
        observation['progress'] = r.progress
        observation['hints'] = r.hints
        observation['lightning'] = r.lightning
        observation['discardpile'] = r.discardpile
        observation['suits'] = r.suits
        observation['deck_size'] = len(r.deck)
        observation['handSize'] = r.handSize
        
        return observation


    def get_legal_actions(self, observation):
        '''Returns a list of the legal game actions'''

        legal_actions = []
        if observation['hints'] < 8:
            discards = [slot for slot in range(observation['handSize'])]
            for discard in discards:
                legal_actions.append(('discard', discard))

        plays = [slot for slot in range(observation['handSize'])]
        for play in plays:
            legal_actions.append(('play', play))
            # these 'plays' need to be actual card objects, not just ints.

        if observation['hints'] > 0:
            for i, hand in enumerate(observation['teammate_hands']):
                #TODO this i needs to be absolute, not relative.
                infos = []
                for card in hand:
                    for info in possible_hints(card):
                        infos.append(info)
                unique_infos = set(infos)
                for info in unique_infos:
                    legal_actions.append(('hint', (i, info)))
                
        return legal_actions
    

    def select_action(self, observation, possible_actions):
        '''Looks at the world and selects an action based on the policy'''
        action = random.choice(possible_actions)
        return action


    def play(self, r):

        observation = self.get_observation(r)
        legal_actions = self.get_legal_actions(observation)
        action = self.select_action(observation, legal_actions)
        # print(action)
        # return(action)
        
        # return self.newest_play(r)


        # cards = r.h[r.whoseTurn].cards
        # progress = r.progress
        # playableCards = get_plays(cards, progress)

        # if playableCards == []:
        #     return 'discard', random.choice(cards)
        # else:
        #     return 'play', random.choice(playableCards)


        me = r.whoseTurn
        cards = r.h[me].cards # don't look!
        # may modify in anticipation of new plays before giving hint
        progress = r.progress.copy()

        # which players already may have plays queued up
        alreadyHinted = {}
        hinterPosition = 1 # turns since my previous play
        if len(r.playHistory) < 4:
            hinterPosition = 5 - len(r.playHistory)
        # first preference is to play hinted cards, then known
        # was I hinted since my last turn?
        # only care about the first hint received in that time
        for playType, playValue in r.playHistory[1-r.nPlayers:]:
            if playType == 'hint':
                target, info = playValue
                # number of turns until hinted player plays
                hintee = (target - me + r.nPlayers) % r.nPlayers
                if target == me:
                    play = self.get_my_newest_hinted(cards, info)
                    if play and possibly_playable(play, r.progress):
                        print(play)
                        return 'play', play
                elif hintee < hinterPosition: # hintee hasn't yet played
                    targetCard = self.get_newest_hinted(r.h[target].cards, info)
                    if targetCard:
                        alreadyHinted[target] = targetCard
            hinterPosition += 1

        # check my knowledge about my cards, are any guaranteed playable?
        myPlayableCards = deduce_plays(cards, progress, r.suits)

        if myPlayableCards != []:
            return 'play', random.choice(myPlayableCards)
 
        if r.hints > 0:
            # look around at each other hand to see if anything is playable
            for i in list(range(me+1, r.nPlayers)) + list(range(0, me)):
                # if i has already been hinted, don't hint them, but consider
                # what they will play before hinting the following player
                if i in alreadyHinted:
                    value, suit = alreadyHinted[i]['name']
                    if progress[suit] == int(value) - 1:
                       progress[suit] += 1
                    continue
                othersCards = r.h[i].cards
                playableCards = get_plays(othersCards, progress)

                if playableCards != []:
                    for card in playableCards:
                        # is there a hint for which this card is the newest?
                        for info in possible_hints(card):
                            if card == self.get_newest_hinted(othersCards, info):
                                return 'hint', (i, info)

        # alright, don't know what to do, let's toss
        return 'discard', self.get_discard(cards)


    def end_game_logging(self):
        """Can be overridden to perform logging at the end of the game"""
        pass
        