from card import Card
import random
short_bonus = [0, 10, 20, 40]
same_color = {'C':'S', 'D':'H', 'H':'D', 'S':'C'}
class Player:
    def __init__(
        self, id, hand, 
        call_first_round_rules,
        call_second_round_rules,
        lead_rules,
        lead_alone_rules,
        follow_rules,
        first_round_threshold=70,
        second_round_threshold=70,
        going_alone_threshold=120 # come back to this
        ):

        for var, name in zip([call_first_round_rules,
        call_second_round_rules,
        lead_rules,
        lead_alone_rules,
        follow_rules], """call_first_round_rules,
        call_second_round_rules,
        lead_rules,
        lead_alone_rules,
        follow_rules""".replace(' ', '').split(',\n')):
            try:
                test = iter(var)
            except:
                print('Variable %s is not iterable!' %name)
                raise(ValueError)

        self.id = id
        self.hand = hand
        self.call_first_round_rules = call_first_round_rules
        self.call_second_round_rules = call_second_round_rules
        self.lead_rules = lead_rules
        self.lead_alone_rules = lead_alone_rules
        self.follow_rules = follow_rules
        self.first_round_threshold = first_round_threshold
        self.second_round_threshold = second_round_threshold
        self.going_alone_threshold = going_alone_threshold
        self.dead = False
    
    def call_first_round(self, board):
        for rule in self.call_first_round_rules:
            call, alone = rule.is_satisfied(board, self)
            if call:
                return call, alone
        return False, None

    def call_second_round(self, board):
        for rule in self.call_second_round_rules:
            suit, alone = rule.is_satisfied(board, self)
            if suit is not None:
                return suit, alone
        return None, None

    def lead(self, board):
        for rule in self.lead_rules:
            c = rule.is_satisfied(board, self)
            if c is not None:
                self.hand.remove(c)
                return c
        c = random.choice(self.hand)
        self.hand.remove(c)
        return c

    def lead_alone(self, board):
        for rule in self.lead_alone_rules:
            c = rule.is_satisfied(board, self)
            if c is not None:
                self.hand.remove(c)
                return c
        c = random.choice(self.hand)
        self.hand.remove(c)
        return c

    def follow(self, board):
        if self.dead:
            del self.hand[0]
            return Card(None, None)

        for rule in self.follow_rules:
            c = rule.is_satisfied(board, self)
            if c is not None:
                self.hand.remove(c)
                return c
        c = random.choice(self.hand)
        self.hand.remove(c)
        return c
    
    def hand_power(self, hand=None):
        # allow the option to pass in a specific hand
        hand = self.hand if hand is None else hand
        base = sum([c.power for c in hand])
        short_suits = set(['C', 'D', 'H', 'S'])
        for c in hand:
            if c.left:
                short_suits.remove(same_color[c.suit]) if same_color[c.suit] in short_suits else None
            else:
                short_suits.remove(c.suit) if c.suit in short_suits else None
        if sum([c.trump for c in hand]) == 0:
            bonus = 0
        else:
            bonus = short_bonus[len(short_suits)]
        
        return base + bonus
    
    def worst_card(self, hand=None):
        # cheap and easy way
        hand = self.hand if hand is None else hand
        power = {c:self.hand_power(hand=[cd.copy() for cd in hand if cd != c]) for c in hand}
        return max(power, key=lambda x: power[x]) # return the card which gives the highest power of the remaining hand

        # maybe write up a way to do this without looping over each card -- give it the rules explicitly
    
    def _order_hand(self, trump_suit = None):
        if trump_suit is not None:
            for c in self.hand:
                c.set_trump(trump_suit)

        new_hand = sorted([c for c in self.hand if c.trump], key=lambda x: x.power, reverse=True)
        for s in ['C', 'D', 'H', 'S']:
            new_hand += sorted([c for c in self.hand if c.suit==s and not c.trump], key=lambda x: x.power, reverse=True)
        
        if trump_suit is not None:
            for c in self.hand:
                c.set_trump(None)

        self.hand = new_hand
    
    def __str__(self):
        return 'Player' + str(self.id)