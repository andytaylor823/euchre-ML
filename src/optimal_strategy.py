from rule import Rule
from player import Player
# rule init: rule(condition, rule_type, name)
# condition: condition(board, player)
first_round_threshold = 72
second_round_threshold = 72
going_alone_threshold = 120 # come back to this
def make_optimal_player(id):
    player = Player(
        id=id,
        hand=[],
        
        call_first_round_rules=get_call_first_round_rules(),
        call_second_round_rules=get_call_second_round_rules(),
        
        lead_rules=get_leading_rules(),
        lead_alone_rules=get_leading_alone_rules(),
        follow_rules=get_follow_rules(),
        
        first_round_threshold=first_round_threshold,
        second_round_threshold=second_round_threshold,
        going_alone_threshold=going_alone_threshold
    )
    return player

def tnum(hand): return(6-len(hand))

###################
# Leading
###################
def get_leading_rules():
	rules = [
		Rule(right_on_3,              'lead', 'right on 3'),
		Rule(offsuit_ace,             'lead', 'offsuit ace'),
		Rule(caller_awkward_spot,     'lead', 'caller awkward spot'),
		Rule(partners_jack,           'lead', 'partner\'s jack'),
		Rule(highest_remaining_trump, 'lead', 'highest remaining trump'),
		Rule(offsuit_king,            'lead', 'offsuit king'),
		Rule(carry_the_team,          'lead', 'carry the team'),
		Rule(mostly_trump,            'lead', 'mostly trump'),
		Rule(best_off_card,           'lead', 'best off card')
	]
	return rules

def right_on_3(board, player):
	if tnum(player.hand) == 3:
		for c in player.hand:
			if c.right:
				return c
	return None

def offsuit_ace(board, player):
	for c in player.hand:
		if c.name == 'A' and not c.trump:
			return c
	return None

# can't put the caller in an awkward spot by leading trump lol
def caller_awkward_spot(board, player):
	if board.caller.id == board._next_pos(player.id):
		led_suits = set([c.suit for c in board.cards_played[::4] if not c.trump])
		possibilities = []
		for c in player.hand:
			if c.trump:
				continue
			if c.suit in led_suits:
				possibilities.append(c)
		if len(possibilities) == 0:
			return None
		return sorted(possibilities, key=lambda x: x.power, reverse=True)[0]
	return None

# TODO fix this for the edge case if other jack was turned down, partner called it, and you have ace
def partners_jack(board, player):
	if board.caller.id == board._partner(player.id):
		for c in player.hand:
			if c.right: return c
			if c.left:  return c
	return None

def _nth_highest_remaining_trump(board, player, n=1):
	trumps_played = set([c.power for c in board.cards_played if c.trump])
	if board.turn_card.left:
		trumps_played.add(board.turn_card.power) # make sure the turn card isn't still leftover trump, verifying it's the left should help
	all_trumps = set([12, 15, 20, 25, 30, 31, 35])
	remaining = sorted([p for p in all_trumps if p not in trumps_played], reverse=True)
	if n > len(remaining):
		return None
	for c in player.hand:
		if c.power == remaining[n-1]:
			return c 
	return None

def highest_remaining_trump(board, player):
	return _nth_highest_remaining_trump(board, player, n=1)


def offsuit_king(board, player):
	for c in player.hand:
		if c.name == 'K':
			if not c.trump:
				return c
	return None

# If you've taken 2 tricks so far and your partner called it,
#   play your lowest so they can play their trump and you keep your trump
def carry_the_team(board, player):
	if board.caller.id == board._partner(player.id):
		if board.ntricks[player.id] == 2:
			if board.ntricks[board._partner(player.id)] < 2:
				if sum([c.trump for c in player.hand]) != 0:
					return min(player.hand, key=lambda x: x.power)
	return None

def mostly_trump(board, player):
	#if sum([c.trump for c in player.hand]) / len(player.hand) >= 0.75:
	#	return max(player.hand, key=lambda x: x.power)
	if sum([c.trump for c in player.hand]) / len(player.hand) >= 0.75:
		return min([c for c in player.hand if c.trump], key=lambda x: x.power)
	return None

def best_off_card(board, player):
    if len([c for c in player.hand if not c.trump]) != 0:
        return max([c for c in player.hand if not c.trump], key=lambda x: x.power)
    return None


###################
# Leading alone
###################
def get_leading_alone_rules():
	rules = [
		Rule(highest_remaining_trump, 'lead', 'highest remaining trump'),
		Rule(offsuit_ace,             'lead', 'offsuit ace'),
		Rule(best_card,               'lead', 'best card')
	]
	return rules

def best_card(board, player):
	return max(player.hand, key=lambda x: x.power)


###################
# Calling 1st round
###################
# do I need anything more here than just checking against the threshold?
# maybe other strategies will call in a different way, so it's fine for now
def get_call_first_round_rules():
	return [Rule(call_first_round, 'call', 'threshold1')]

def call_first_round(board, player):

	for c in player.hand:
		c.set_trump(board.turn_card.suit)
	
	if player.id == board.dealer.id:
		hand = [c for c in player.hand if c != player.worst_card()] + [board.turn_card]
	else:
		hand = player.hand
	power = player.hand_power(hand)
	#                                                   # dealer is.....
	if player.id == board.dealer.id:                    bonus = 0    # self
	elif player.id == board._partner(board.dealer.id):  bonus = 0.5  # partner
	elif player.id == board._next_pos(board.dealer.id): bonus = -0.3 # to my right
	else:                                               bonus = -0.4 # to my left
	power += board.turn_card.power * bonus

	# remove all trump
	for c in player.hand:
		c.set_trump(None)
	
	#if power >= board.going_alone_threshold:
	if power >= player.going_alone_threshold:
		return True, True
	#return power >= board.first_round_threshold, False
	return power >= player.first_round_threshold, False


###################
# Calling 2nd round
###################
# do I need anything more here than just checking against the threshold?
def get_call_second_round_rules():
	return [Rule(call_second_round, 'call', 'threshold2')]
def call_second_round(board, player):
	powers = {}
	for s in ['C', 'D', 'H', 'S']:
		if s == board.turn_card.suit:
			powers[s] = -1
			continue
		for c in player.hand:
			c.set_trump(s)
		powers[s] = player.hand_power()
	
	suit, max_power = max(powers.items(), key=lambda x: x[1])
	#if max_power > board.going_alone_threshold:
	if max_power > player.going_alone_threshold:
		return suit, True
	elif player.id == board.dealer.id:
		return suit, False
	#elif max_power > board.second_round_threshold:
	elif max_power >= player.second_round_threshold:
		return suit, False
	else:
		return None, False

###################
# Following
###################
def get_follow_rules():
	return [Rule(follow, 'follow', 'basic follow')]
def follow(board, player):
	# come back to this
	if board.going_alone:
		pass

	teamwinner, legal, winning_card, led_card, have_highest_trump, followsuit, have_trump, ntricks_team, ntricks_remaining = _current_state(board, player)
	n, c2_above, c3_above = _trump_spot_winning_card(board, player, teamwinner, winning_card)

	can_win, highest, lowest, lowest_winning = _key_cards(board, player, legal)

	if not can_win:						                        return(lowest)
	if not teamwinner:
		if led_card.trump:
			if board.caller.id == board._partner(player.id):    return(highest)
			elif board.caller.id == player.id:                  return(highest)
			else:                                               return(lowest_winning)
		elif highest.suit==led_card.suit and not highest.left:	return(highest)
		else:								                    return(lowest_winning)
	
	# If you can't win the trick, play your lowest legal card
	
	# If your teammate **doesn't** have it:
		# If trump was led:
			# If your teammate called trump       		:	highest
			# If you called trump                       :   highest
			# If your team did not call trump 			:	lowest winning
		# If you're following an off-suit	  			:	highest
		# If you're trumping an off-suit	  			:	lowest winning
	
	else:
		if len(board.tricks[board.tnum-1]) == 3:				return(lowest)
		if led_card.trump:
			if have_highest_trump:
				if n != 2:					                    return(highest)
				else:						                    return(lowest)
			else:
				if c2_above is not None:				        return(c2_above)
				elif c3_above is not None:				        return(c_3_above)
				else:						                    return(lowest)
				
	# If your teammate **does** have it:
		# If you're the last person		  			            :	lowest
		# If trump was led:
			# If you have the top card:
				# If your partner can be beat			        :	highest
				# If your partner can't be beat			        :	lowest
			# If you don't have the top card:
				# If you have the one two above your partner	:	that one
				# If you have the one three above your partner	:	that one
				# Else						                    :	lowest
		
		else:
			if winning_card.name == 'A':				            return(lowest)
			else:
				if followsuit:					                    return(highest)
				else:
					if not have_trump:			                    return(lowest)
					else:
						if ntricks_team + ntricks_remaining >= 3:   return(lowest_winning)
						else:				                        return(lowest)
			
		# If an off-suit was led:
			# If your partner is     winning it with an ace		:	lowest
			# If your partner is not winning it with an ace:
				# If you have to follow suit			:	highest
				# If you don't have to follow suit:
					# If you can't trump it			: 	lowest
					# If you can trump it:
						# If n_tricks_won + n_trump_in_hand >= 3:	lowest winning
						# If you need that king to win the trick:	lowest

def _current_state(board, player):
	current_trick = board.current_trick
	led_card = current_trick[0]

	legal = _legal_hand(board, player)

	winning_card = board.winning_card
	if len(current_trick) < 2:
		teamwinner = False
	else:
		teamwinner = winning_card==current_trick[-2]
	
	have_highest_trump = highest_remaining_trump(board, player)
	if board.current_trick[0].trump:
		followsuit = any([c.trump for c in legal])
	else:
		followsuit = legal[0].suit==current_trick[0].suit # thankfully legal hand makes this faster
	
	have_trump = any([c.trump for c in legal])
	n_tricks_won_team = board.ntricks[player.id] + board.ntricks[board._partner(player.id)]
	n_tricks_remaining = len(player.hand)

	return teamwinner, legal, winning_card, led_card, have_highest_trump, followsuit, have_trump, n_tricks_won_team, n_tricks_remaining

def _legal_hand(board, player):
	# check to make sure not leading
	if len(board.cards_played) % 4 == 0:
		return player.hand 
	led_card = board.cards_played[::4][-1]
	# check for following suit
	if led_card.trump:
		follow = [c for c in player.hand if c.trump]
	else:
		follow = [c for c in player.hand if c.suit == led_card.suit and not c.trump]

	if len(follow) != 0:
		return follow
	return player.hand


# returns the number of unseen trump cards higher than the current winning card
def _trump_spot_winning_card(board, player, teamwinner, winning_card):

	n, c2_above, c3_above = None, None, None
	if winning_card.trump:
		if teamwinner:
			for i in range(7):
				c = _nth_highest_remaining_trump(board, player, n=i+1)
				if c == winning_card:
					n=i+1
					break
	if n is not None:
		if n > 2:
			c2_above = _nth_highest_remaining_trump(board, player, n=n-2)
		if n > 3:
			c3_above = _nth_highest_remaining_trump(board, player, n=n-3)
	return n, c2_above, c3_above

def _key_cards(board, player, legal):

	lowest = player.worst_card(hand=legal)
	highest = max(legal, key=lambda x: x.power)
	if board.winning_card.trump:
		# catches if (1) have to follow led non-trump suit and (2) can't beat the top trump
		if highest.power < board.winning_card.power:
			can_win, lowest_winning = False, None
		else:
			can_win, lowest_winning = True, min([c for c in legal if c.power > board.winning_card.power], key=lambda x: x.power)
	else:
		# do we have to follow suit?
		if legal[0].suit == board.winning_card.suit and not legal[0].left:
			# all cards in legal must now be of the led suit
			if highest.power < board.winning_card.power:
				can_win, lowest_winning = False, None
			else:
				can_win, lowest_winning = True, min([c for c in legal if c.power > board.winning_card.power], key=lambda x: x.power)
		else:
			# we can't follow suit -- can we trump it?
			if highest.power < 12:
				can_win, lowest_winning = False, None
			else:
				can_win, lowest_winning = True, min([c for c in legal if c.trump], key=lambda x: x.power)
	
	return can_win, highest, lowest, lowest_winning
