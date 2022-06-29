from copy import deepcopy
from card import Card
from player import Player
import optimal_strategy as opt
import store_data
import show_board

import random
import sys
import os

# unused as of 06/29/2022
#full_names = {'C':'Clubs', 'D':'Diamonds', 'H':'Hearts', 'S':'Spades'}
#name_to_writeout = {'9': [0,0,0,0,0],
#                    'T': [1,0,0,0,0],
#                    'J': [0,1,0,0,0],
#                    'Q': [0,0,1,0,0],
#                    'K': [0,0,0,1,0],
#                    'A': [0,0,0,0,1]}
# Position options: 0, 1, 2, 3.
# Imagine 0 as sitting at west, then going clockwise, ending with 3 at south
class Board:
    def __init__(self, p0=None, p1=None, p2=None, p3=None, seed=None):
        if len(sys.argv) < 1:   self.in_kernel = True # from command line
        else:                   self.in_kernel = 'ipykernel_launcher.py' in sys.argv[0]

        random.seed(seed)
        if p0 is None: p0 = opt.make_optimal_player(0)
        if p1 is None: p1 = opt.make_optimal_player(1)
        if p2 is None: p2 = opt.make_optimal_player(2)
        if p3 is None: p3 = opt.make_optimal_player(3)
        self.players = [p0, p1, p2, p3]
        self.dealer = random.choice(self.players)
        self.leader = self.players[self._next_pos(self.dealer.id)]
        
        self.reset_hand()
        
        self.show = True
        self.store = True
        self.points = [0, 0] # players 0 & 2 get ix 0, players 1 & 3 get ix 1
        self.data = []
        self.results = []
        self.header = []

    # TODO work this into self.close_hand() to remove unnecessary duplication
    def reset_hand(self):
        self.turn_card = None
        self.trump_suit = None
        self.kitty = []
        self.starting_hands = []

        self.caller = None
        self.winner = None
        self.winners = []
        self.current_player = self.leader
        self.winning_card = None

        self.going_alone = False
        self.called_first_round = None

        self.ntricks = [0,0,0,0]
        self.cards_played = []
        self.tricks = [[], [], [], [], []]
        self.current_trick = []
        self.tnum = 1

        self.points_this_round = [0,0]
        self.result = None


    def play_hand(self, show=False, seed=None):
        self.show = show
        self.reset_hand()
        self.deal(seed)
        self._show()
        self.call_trump()
        for tnum in range(1,6):
            for _ in range(4):
                self.play_card()
                self.update_winner()
                self.advance_player()
                self._show()
            self.close_trick()
        self.close_hand()
        #self._show()

    def play_game(self, show=True):
        while max(self.points) < 10:
            self.play_hand(show)


    def deal(self, seed=None):
        deck = self._create_deck()
        random.seed(seed) # if seed = None, this is still random
        random.shuffle(deck)
        for i in range(4):
            self.players[i].hand = deck[(5*i):(5*(i+1))]
        self.turn_card = deck[20]
        self.kitty = deck[21:]
        for p in self.players:
            p._order_hand(trump_suit=self.turn_card.suit)
            self.starting_hands.append(p.hand)
        if seed is not None:
            self.dealer = random.choice(self.players)
            self.leader = self.players[self._next_pos(self.dealer.id)]
    
    def call_trump(self):
        for _ in range(4):
            order_up, alone = self.current_player.call_first_round(self)
            if order_up:
                break
            self.advance_player()
        if order_up:
            self.caller = self.current_player
            self.current_player = self.leader
            self.trump_suit = self.turn_card.suit
            self.called_first_round = True
            self.apply_trump()

            self.dealer.hand.remove(self.dealer.worst_card())
            self.dealer.hand += [self.turn_card]
            self.dealer._order_hand()

        else:
            self.current_player = self.leader
            self.called_first_round = False
            for _ in range(4):
                suit, alone = self.current_player.call_second_round(self)
                if suit is not None:
                    break
                self.advance_player()
            if suit is None:
                suit = self._stick_the_dealer()
                self.current_player = self.dealer

            self.caller = self.current_player
            self.current_player = self.leader
            self.trump_suit = suit
            self.apply_trump()

        # TODO: figure this out            
        if alone:
            self.players[self._partner(self.caller.id)].dead = True
            self.players[self._partner(self.caller.id)].hand = [Card(None, None)]*5 # maybe isn't needed
            self.going_alone = True
            if self.caller.id == self.players[self._partner(self.leader.id)].id: # check if leader is now not leader
                self.leader = self.players[self._next_pos(self.leader.id)]
                self.current_player = self.leader
            #self.show = True

    def apply_trump(self):
        for player in self.players:
            for c in player.hand:
                c.set_trump(self.trump_suit)
            player._order_hand()
        self.turn_card.set_trump(self.trump_suit)
        for h in self.starting_hands:
            for c in h:
                c.set_trump(self.trump_suit)
        #for c in self.kitty:
        #   c.set_trump(self.trump_suit)
    
    def play_card(self):
        if len(self.current_trick) == 0:
            if self.going_alone:
                if self.caller.id == self.current_player.id:
                    c = self.current_player.lead_alone(self)
                else:
                    c = self.current_player.lead(self)
            else:
                c = self.current_player.lead(self)
        else:
            c = self.current_player.follow(self)
        # card is already removed from the player's hand

        self.cards_played.append(c)
        self.current_trick.append(c)
        self.tricks[self.tnum-1].append(c)
    
    def update_winner(self):
        beat_it = False
        if len(self.current_trick) == 1:
            beat_it = True
        else:
            if self.winning_card.trump:
                if self.current_trick[-1].power > self.winning_card.power:
                    beat_it = True
            elif self.current_trick[-1].trump:
                beat_it = True
            else:
                # neither of the two cards are trump
                if self.current_trick[-1].suit == self.winning_card.suit:
                    if self.current_trick[-1].power > self.winning_card.power:
                        beat_it = True 
        if beat_it:
            self.winner = self.current_player
            self.winning_card = self.current_trick[-1]
        
    def advance_player(self):
        if len(self.current_trick) == 4:
            self.current_player = self.winner
        else:
            self.current_player = self.players[self._next_pos(self.current_player.id)]

    def close_trick(self):
        self.tnum += 1

        self.ntricks[self.winner.id] += 1
        self.winners.append(self.winner)

        self.leader = self.winner
        self.current_player = self.leader
        
        self.current_trick = []
        self.winning_card = None
        self.winner = None

    def close_hand(self):
        self._points()
        self._show()
        self._store_data()

        self.turn_card = None
        self.trump_suit = None
        self.kitty = []
        self.starting_hands = []

        if self.going_alone:
            self.players[self._partner(self.caller.id)].dead = False
            self.players[self._partner(self.caller.id)].hand = []
            self.going_alone = False
            self.show = False

        self.dealer = self.players[self._next_pos(self.dealer.id)]
        self.leader = self.players[self._next_pos(self.dealer.id)]
        self.caller = None
        self.winner = None
        self.winners = []
        self.current_player = self.leader
        self.winning_card = None
        self.going_alone = False
        self.called_first_round = None
        self.result = None

        self.ntricks = [0,0,0,0]
        self.cards_played = []
        self.tricks = [[], [], [], [], []]
        self.current_trick = []
        self.tnum = 1

        

    def _create_deck(self):
        names = ['9', 'T', 'J', 'Q', 'K', 'A']
        suits = ['C', 'D', 'H', 'S']
        return [Card(n,s) for n in names for s in suits]

    def _next_pos(self, pos): return (pos+1)%4
    def _prev_pos(self, pos): return (pos-1)%4
    def _partner(self, pos):  return (pos+2)%4

    def _stick_the_dealer(self):
        powers = {}
        for suit in ['C', 'D', 'H', 'S']:
            if suit == self.turn_card.suit:
                continue
            for c in self.dealer.hand:
                c.set_trump(suit)
            powers[suit] = self.dealer.hand_power()
            for c in self.dealer.hand:
                c.set_trump(None)
        return max(powers, key=lambda x: powers[x])
    
    def _points(self):
        ntricks = [sum([w.id%2 == i for w in self.winners]) for i in range(2)]
        callers, winners = self.caller.id%2, self.caller.id%2
        if ntricks[callers] == 5: points, result = (4 if self.going_alone else 2), 'Sweep'
        elif ntricks[callers] >= 3: points, result = 1, 'Single'
        else: points, result, winners = 2, 'EUCHRE', 1-callers
        
        by_against = 'by' if result != 'EUCHRE' else 'against'
        if self.going_alone:
            self.result = f'Loner {result[0].lower() + result[1:]} {by_against} Player {self.caller.id}'
        else:
            self.result = f'{result} {by_against} Players {self.caller.id} and {self._partner(self.caller.id)}'

        self.points[winners] += points
        self.points_this_round[winners] += points
        
        # Deprecated as of 06/29/2022
        old="""
        if self.caller.id%2 == 0:
            if self.going_alone:
                if ntricks[0] == 5:
                    self.points[0] += 4
                    self.points_this_round[0] += 4
                    self.result = 'Loner sweep by Player %i' %self.caller.id
                elif ntricks[0] >= 3:
                    self.points[0] += 1
                    self.points_this_round[0] += 1
                    self.result = 'Loner single by Player %i' %self.caller.id
                else:
                    self.points[1] += 2
                    self.points_this_round[1] += 2
                    self.result = 'Loner EUCHRE against Player %i' %self.caller.id
            else:
                if ntricks[0] == 5:
                    self.points[0] += 2
                    self.points_this_round[0] += 2
                    self.result = 'Sweep by Players %i and %i' %(self.caller.id, self._partner(self.caller.id))
                elif ntricks[0] >= 3:
                    self.points[0] += 1
                    self.points_this_round[0] += 1
                    self.result = 'Single by Players %i and %i' %(self.caller.id, self._partner(self.caller.id))
                else:
                    self.points[1] += 2
                    self.points_this_round[1] += 2
                    self.result = 'EUCHRE against Players %i and %i' %(self.caller.id, self._partner(self.caller.id))
        else:
            if self.going_alone:
                if ntricks[1] == 5:
                    self.points[1] += 4
                    self.points_this_round[1] += 4
                    self.result = 'Loner sweep by Player %i' %self.caller.id
                elif ntricks[1] >= 3:
                    self.points[1] += 1
                    self.points_this_round[1] += 1
                    self.result = 'Loner single by Player %i' %self.caller.id
                else:
                    self.points[0] += 2
                    self.points_this_round[0] += 2
                    self.result = 'Loner EUCHRE against Player %i' %self.caller.id
            else:
                if ntricks[1] == 5:
                    self.points[1] += 2
                    self.points_this_round[1] += 2
                    self.result = 'Sweep by Players %i and %i' %(self.caller.id, self._partner(self.caller.id))
                elif ntricks[1] >= 3:
                    self.points[1] += 1
                    self.points_this_round[1] += 1
                    self.result = 'Single by Players %i and %i' %(self.caller.id, self._partner(self.caller.id))
                else:
                    self.points[0] += 2
                    self.points_this_round[0] += 2
                    self.result = 'EUCHRE against Players %i and %i' %(self.caller.id, self._partner(self.caller.id))
        """
        
    # Export to a separate file to make this file cleaner
    def _show(self, asvar=False):
        return show_board.show(self, asvar)


    def _run_quiet(self):
        self.show = False
    
    # Export to a separate file to make this filecleaner
    def _store_data(self):
        if not self.store: return None
        
        data, header = store_data.get_data(self)
        self.data.append(data)
        self.results.append(self.result)
    
    @staticmethod
    def data_to_readable(gameline, header=[]):
        return store_data.data_to_readable(gameline, header)
    
    def writeout(self, folder, keep_results=False):
        if not self.store: return None
        
        # Make the folder if doesn't already exist
        if not os.path.isdir(folder):
            print('Making folder:', folder)
            if folder[0] != '/': print('Relative to cwd:', os.getcwd())
            os.mkdir(folder)
            
        # Make the results folder if doesn't already exist and is desired
        if keep_results and 'results' not in os.listdir(folder): os.mkdir(folder + '/results')
        
        prename = str(len(self.data)) + '_hands_'
        datafiles = os.listdir(folder)
        
        # Find the first index unused file
        i = 0
        while True:
            filename = folder + '/' + prename + str(i).zfill(3) + '.csv'
            results_file = folder + '/results/' + str(len(self.data)) + '_results_' + str(i).zfill(3) + '.txt'
            if filename.split('/')[-1] not in datafiles:
                break
            i += 1

        # Write the data
        with open(filename, 'w') as f:
            f.write(','.join(self.header) + '\n')
            for hand in self.data:
                f.write(','.join([str(val) for val in hand]) + '\n')
        
        # If desired, write the results
        if keep_results:
            with open(results_file, 'w') as f:
                f.write('\n'.join(self.results))
        
        # cleanup
        self.data = []
        self.header = []
        self.results = []

    def copy(self):
        return deepcopy(self)
    
