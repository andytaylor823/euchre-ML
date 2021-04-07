from copy import deepcopy
from card import Card
from player import Player
import optimal_strategy
import random
import sys
import os

full_names = {'C':'Clubs', 'D':'Diamonds', 'H':'Hearts', 'S':'Spades'}
name_to_writeout = {'9': [0,0,0,0,0],
                    'T': [1,0,0,0,0],
                    'J': [0,1,0,0,0],
                    'Q': [0,0,1,0,0],
                    'K': [0,0,0,1,0],
                    'A': [0,0,0,0,1]}
suit_to_writeout = {'C':[0,0,0], 'D':[1,0,0], 'H':[0,1,0], 'S':[0,0,1]}
# Position options: 0, 1, 2, 3.
# Imagine 0 as sitting at west, then going clockwise, ending with 3 at south
class Board:
    def __init__(self, p0=None, p1=None, p2=None, p3=None):
        if len(sys.argv) < 1:   self.in_kernel = True # from command line
        else:                   self.in_kernel = 'ipykernel_launcher.py' in sys.argv[0]

        if p0 is None:
            p0 = self._make_optimal_player(0)
        if p1 is None:
            p1 = self._make_optimal_player(1)
        if p2 is None:
            p2 = self._make_optimal_player(2)
        if p3 is None:
            p3 = self._make_optimal_player(3)

        self.players = [p0, p1, p2, p3]
        self.turn_card = None
        self.trump_suit = None
        self.kitty = []
        self.starting_hands = []

        self.dealer = random.choice(self.players)
        self.leader = self.players[self._next_pos(self.dealer.id)]
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

        self.points = [0, 0] # players 0 & 2 get ix 0, players 1 & 3 get ix 1
        self.points_this_round = [0,0]
        self.result = None
        self.results = []

        self.show = True
        self.store = True
        self.data = []
        self.header = []

    def play_hand(self, show=False):
        self.show = show
        self.deal()
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
        self._show()

    def play_game(self, show=True):
        while max(self.points) < 10:
            self.play_hand(show)


    def deal(self):
        deck = self._create_deck()
        random.shuffle(deck)
        for i in range(4):
            self.players[i].hand = deck[(5*i):(5*(i+1))]
        self.turn_card = deck[20]
        self.kitty = deck[21:]
        for p in self.players:
            p._order_hand(trump_suit=self.turn_card.suit)
            self.starting_hands.append(p.hand)
        self.points_this_round = [0,0]
    
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
                c = self.current_player.lead_alone(self)
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

        


    def _make_optimal_player(self, id):
        player = Player(
            id=id,
            hand=[],
            call_first_round_rules=optimal_strategy.get_call_first_round_rules(),
            call_second_round_rules=optimal_strategy.get_call_second_round_rules(),
            lead_rules=optimal_strategy.get_leading_rules(),
            lead_alone_rules=optimal_strategy.get_leading_alone_rules(),
            follow_rules=optimal_strategy.get_follow_rules()
        )
        return player


    def _create_deck(self):
        names = ['9', 'T', 'J', 'Q', 'K', 'A']
        suits = ['C', 'D', 'H', 'S']
        deck = []
        for n in names:
            for s in suits:
                deck.append(Card(n, s))
        return deck

    def _next_pos(self, pos):
        return (pos+1)%4
    def _prev_pos(self, pos):
        return (pos-1)%4
    def _partner(self, pos):
        return (pos+2)%4

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

    def _show(self, asvar=False):
        if not self.show:
            return

        if self.result is not None:
            lines = ['Hand is finished!']
            lines.append(self.result)
            lines.append('Players 0/2 score: %i (%i tricks)\nPlayers 1/3 score: %i (%i tricks)' \
                %(self.points[0], self.ntricks[0]+self.ntricks[2], self.points[1], self.ntricks[1]+self.ntricks[3]))
            print('\n'.join(lines))

            if asvar: return lines
            else:     return None

        p3 = self.dealer
        p0 = self.players[self._next_pos(p3.id)]
        p1 = self.players[self._next_pos(p0.id)]
        p2 = self.players[self._next_pos(p1.id)]

        all_space = ' '
        zero_placeholder_space = ' '
        zero_to_hand_space = ' '
        zerohand_placeholder_space = '  '
        zerohand_to_onethreehand_space = ' '
        onethreehand_placeholder_space = ' '.join(['  ' for _ in range(5)])
        onethreehand_to_twohand_space = zerohand_to_onethreehand_space # mirror
        twohand_placeholder_space = zerohand_placeholder_space
        hand_to_two_space = zero_to_hand_space
        two_placeholder_space = ' '

        all_zero_space = all_space
        all_onethree_space = all_zero_space + zero_placeholder_space + zero_to_hand_space + zerohand_placeholder_space + zerohand_to_onethreehand_space
        all_two_space = all_onethree_space + onethreehand_placeholder_space + onethreehand_to_twohand_space

        zerohand_to_onethree_cardplayed_space = zerohand_to_onethreehand_space + ' '.join(['  ' for _ in range(2)]) + ' '
        zerohand_to_zero_cardplayed_space = zerohand_to_onethreehand_space + ' '.join(['  ' for _ in range(1)]) + ' '
        zerohand_to_two_cardplayed_space = zerohand_to_onethreehand_space + ' '.join(['  ' for _ in range(3)]) + ' '
        zero_cardplayed_to_two_cardplayed_space = ' ' + ' '.join(['  ' for _ in range(1)]) + ' '
        zero_cardplayed_to_twohand_space = ' ' + ' '.join(['  ' for _ in range(3)]) + onethreehand_to_twohand_space

        lines = ['']
        # first, just the number 1
        lines.append(all_onethree_space + ''.join([' ' for _ in range(int(len(onethreehand_placeholder_space)/2))]) + str(p1.id))
        # next, player 1's hand
        lines.append(all_onethree_space + ' '.join([str(c) for c in p1.hand]) + ' ' +  ' '.join(['--' for _ in range(5-len(p1.hand))]))
        # next, a blank row
        lines.append(' ')
        # next, player 0 and player 2 hand
        # this gets a bit hairy with the played cards
        for i in range(5):
            s = all_zero_space
            if i == 2: s += str(p0.id)
            else:      s += zero_placeholder_space
            s += zero_to_hand_space 

            if i < len(p0.hand): s += str(p0.hand[i])
            else:                s += '--'

            if i == 1:
                if len(p1.hand) < 6-self.tnum:
                    s += zerohand_to_onethree_cardplayed_space + str(self.current_trick[(p1.id-self.leader.id)%4]) + zerohand_to_onethree_cardplayed_space # mirror
                else:
                    s += zerohand_to_onethreehand_space + onethreehand_placeholder_space + onethreehand_to_twohand_space

            elif i == 2:
                if len(p0.hand) < 6-self.tnum:
                    s += zerohand_to_zero_cardplayed_space + str(self.current_trick[(p0.id-self.leader.id)%4])
                    if len(p2.hand) < 6-self.tnum:
                        s += zero_cardplayed_to_two_cardplayed_space + str(self.current_trick[(p2.id-self.leader.id)%4]) + zerohand_to_zero_cardplayed_space # mirror
                    else:
                        s += zero_cardplayed_to_twohand_space
                elif len(p2.hand) < 6-self.tnum:
                    s += zerohand_to_two_cardplayed_space + str(self.current_trick[(p2.id-self.leader.id)%4]) + zerohand_to_zero_cardplayed_space # mirror
                else:
                    s += zerohand_to_onethreehand_space + onethreehand_placeholder_space + onethreehand_to_twohand_space

            elif i == 3:
                if len(p3.hand) < 6-self.tnum:
                    s += zerohand_to_onethree_cardplayed_space + str(self.current_trick[(p3.id-self.leader.id)%4]) + zerohand_to_onethree_cardplayed_space # mirror
                else:
                    s += zerohand_to_onethreehand_space + onethreehand_placeholder_space + onethreehand_to_twohand_space

            else:
                s += zerohand_to_onethreehand_space + onethreehand_placeholder_space + onethreehand_to_twohand_space

            if i < len(p2.hand): s += str(p2.hand[i])
            else:                s += '--'

            if i == 2: s += hand_to_two_space + str(p2.id)
            s += '\n'
            lines.append(s)

        # next, player 3's hand
        lines.append(all_onethree_space + ' '.join([str(c) for c in p3.hand]) + ' ' +  ' '.join(['--' for _ in range(5-len(p3.hand))]))
        # next, the number 3
        lines.append(all_onethree_space + ''.join([' ' for _ in range(int(len(onethreehand_placeholder_space)/2))]) + str(p3.id))
        # a line break, for space
        lines.append('')



        # add in global stuff, can come back to this
        lines.append('Turn card: ' + str(self.turn_card) + ', Player %i is dealer' %self.dealer.id)
        if self.trump_suit is not None:
            lines.append('Trump suit: *' + str(full_names[self.trump_suit]).upper() + '* (called %s round by Player %i)'\
                     %('first' if self.called_first_round else 'second', self.caller.id))
        if self.going_alone:
            lines.append('THIS PLAYER IS GOING ALONE')

        if len(self.cards_played) > 0:
            lines.append('')
            lines.append('Player %i led, and Player %i is winning' %(self.leader.id, self.winner.id))

        lines.append('Players 0/2 score: %i (%i tricks currently)\nPlayers 1/3 score: %i (%i tricks currently)' \
                %(self.points[0], self.ntricks[0]+self.ntricks[2], self.points[1], self.ntricks[1]+self.ntricks[3]))
        
        # final line break to close it out
        lines.append('\n')


        print('\n'.join(lines))
        x = ''
        while x.lower() not in ['x', 'c']:
            x = input('Enter "c" to continue, "x" to exit: ')

        if x.lower() == 'x':
            if self.in_kernel:
                sys.exit()
            else:
                exit()
        if asvar:
            return lines


    def _run_quiet(self):
        self.show = False
    
    def _store_data(self):
        if not self.store:
            return None
        
        # how am I going to store the data?
        # each card -- when stored as via OHE -- takes up 8 values (6-1 for name and 4-1 for suit)
        # alternatively, can store card's power (1) and suit (3), bringing each card to 4 values
        # write out each player's starting hand, then write out some global stuff, then finish with the order of the cards played and the order of who won each trick

        data = []
        # write each player's hand
        # Total values after this: 4 x 20 = 80
        for i in range(4):
            pos = (i-self.dealer.id+1)%4 # start to the left of the dealer
            data += [val for c in self.starting_hands[pos] for val in [c.power] + [issuit for issuit in suit_to_writeout[c.suit]]]
        # write some global stuff:
        # turn_card power & suit (1 + 3) trump suit (3), caller position (relative to dealer; 1), round called in (1), alone (1), 
        #       who won each trick (relative to dealer; 5), number of points for team 0/2 and 1/3 (relative to dealer; 2)
        # Total values after this: 80 + 17 = 97
        data += [Card(self.turn_card.name, self.turn_card.suit, trump_suit=self.turn_card.suit).power] + [v for v in suit_to_writeout[self.turn_card.suit]] # make sure the power is affected by trump
        data += [v for v in suit_to_writeout[self.trump_suit]]
        data += [(self.caller.id-self.dealer.id-1)%4] # subtract one so that if caller-position here is 0, it's the dealer's left
        data += [2-int(self.called_first_round)]
        data += [int(self.going_alone)]
        data += [(w.id-self.dealer.id-1)%4 for w in self.winners]
        data += [self.points_this_round[(self.dealer.id+1)%2], self.points_this_round[self.dealer.id%2]]
        # now just write out the order of all the cards played -- string (card + player id) is fine
        # include the first word of the result as well ("EUCHRE", "Single", "Sweep", "Loner")
        # Total values after all this: 97 + 21 = 118
        data += [str(self.cards_played[i]) + str(i) for i in range(4)] # if dealer is 3, first trick is always 0 - 1 - 2 - 3
        data += [str(self.cards_played[4*j+i]) + str((i+self.winners[j-1].id-self.dealer.id-1)%4) for j in range(1,5) for i in range(4)]
        data += [self.result.split()[0]]
        data += [(i+self.dealer.id+1)%4 for i in range(4)]

        if self.header == []:
            header = []
            # writes out alternating e.g. "p2c3" and ["isD", "isH", "isS"] then moves onto "p2c4", then eventually gets to "p3c1", etc
            header += [val for player in range(4) for card in range(1,6) for val in ['p'+str(player)+'c'+str(card)] + ['p'+str(player)+'c'+str(card)+issuit for issuit in ['isD', 'isH', 'isS']]]
            header += ['TC_power'] + ['TC_is' + s for s in ['D', 'H', 'S']]
            header += ['trump_is' + c for c in ['D', 'H', 'S']]
            header += ['caller', 'round', 'alone']
            header += ['winner' + str(i) for i in range(1,6)]
            header += ['points02', 'points13']
            header += ['played' + str(i) for i in range(1,21)]
            header += ['result']
            header += ['p'+str(i)+'trueid' for i in range(4)]
            self.header = header

        self.data.append(data)
        self.results.append(self.result)
    
    def writeout(self, folder='stored_runs', keep_results=False, ROOT_DIR=os.getcwd()+'/'):
        if not self.store:
            return None
        ROOT_DIR = ROOT_DIR + '/' if ROOT_DIR[-1] != '/' else ROOT_DIR
        #folder = os.path.join(ROOT_DIR, folder)
        if folder[:len(ROOT_DIR)] != ROOT_DIR:
            folder = ROOT_DIR + folder

        if folder[len(ROOT_DIR):] not in os.listdir(ROOT_DIR):
            os.mkdir(folder)
        if keep_results:
            if 'results' not in os.listdir(folder):
                os.mkdir(folder + '/results')
        
        prename = str(len(self.data)) + '_hands_'
        datafiles = os.listdir(folder)
        
        i = 0
        while True:
            filename = folder + '/' + prename + str(i).zfill(3) + '.csv'
            results_file = folder + '/results/' + str(len(self.data)) + '_results_' + str(i).zfill(3) + '.txt'
            if filename.split('/')[-1] not in datafiles:
                break
            i += 1

        with open(filename, 'w') as f:
            f.write(','.join(self.header) + '\n')
            for hand in self.data:
                f.write(','.join([str(val) for val in hand]) + '\n')
        
        if keep_results:
            with open(results_file, 'w') as f:
                f.write('\n'.join(self.results))
        
        # cleanup
        self.data = []
        self.header = []
        self.results = []

    def copy(self):
        return deepcopy(self)
    
