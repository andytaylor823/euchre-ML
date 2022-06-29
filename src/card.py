# Name options: '9', 'T', 'J', 'Q', 'K', 'A'
# Suit options: 'C', 'D', 'H', 'S'
from copy import deepcopy
same_color = {'C':'S', 'D':'H', 'H':'D', 'S':'C'}
trump_power = {'9':12, 'T':15, 'Q':20, 'K':25, 'A':30, 'left':31, 'right':35, None:0}
non_trump_power = {'9':1, 'T':2, 'J':3, 'Q':4, 'K':5, 'A':10, None:0}
class Card:
    def __init__(self, name, suit, trump_suit=None):
        self.name, self.suit = name, suit
        self.set_trump(trump_suit)

    def set_trump(self, trump_suit):
        if trump_suit is None:
            self.trump = False
        else:
            if self.suit == trump_suit:
                self.trump = True
            else:
                self.trump = (self.name == 'J') and (self.suit == same_color[trump_suit])

        if self.trump:
            if self.name == 'J':
               self.right = self.suit==trump_suit
               self.left = self.suit==same_color[trump_suit] 
            else:
                self.right, self.left = False, False
        else:
            self.right, self.left = False, False

        self._set_power()
    
    def _set_power(self):
        if self.trump:
            if self.right:
                self.power = 35
            elif self.left:
                self.power = 31
            else:
                self.power = trump_power[self.name]
        else:
            self.power = non_trump_power[self.name]

    def copy(self):
        return deepcopy(self) 

    def __eq__(self, other):
        if other is None: return False
        return (other.suit==self.suit) and (other.name==self.name)

    def __str__(self):
        if self.name is None:
            return '--'
        return str(self.name) + str(self.suit)

    def __repr__(self):
        if self.name is None:
            return '--'
        return str(self.name) + str(self.suit)

    def __hash__(self):
        return hash(self.name) + hash(self.suit)