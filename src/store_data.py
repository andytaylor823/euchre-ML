from card import Card
import numpy as np
suit_to_writeout = {'C':[0,0,0], 'D':[1,0,0], 'H':[0,1,0], 'S':[0,0,1]}
def get_data(board):
    # how am I going to store the data?
    # each card -- when stored as via OHE -- takes up 8 values (6-1 for name and 4-1 for suit)
    # alternatively, can store card's power (1) and suit (3), bringing each card to 4 values
    # write out each player's starting hand, then write out some global stuff, then finish with the order of the cards played and the order of who won each trick

    data = []
    # write each player's hand
    # Total values after this: 4 x 20 = 80
    for i in range(4):
        pos = (i+board.dealer.id+1)%4 # start to the left of the dealer
        data += [val for c in board.starting_hands[pos] for val in [c.power] + [issuit for issuit in suit_to_writeout[c.suit]]]
        
    # write some global stuff:
    # turn_card power & suit (1 + 3) trump suit (3), caller position (relative to dealer; 1), round called in (1), alone (1), 
    #       who won each trick (relative to dealer; 5), number of points for team 0/2 and 1/3 (relative to dealer; 2)
    # Total values after this: 80 + 17 = 97
    data += [Card(board.turn_card.name, board.turn_card.suit, trump_suit=board.turn_card.suit).power] + \
                [v for v in suit_to_writeout[board.turn_card.suit]] # make sure the power is affected by trump
    data += [v for v in suit_to_writeout[board.trump_suit]]
    data += [(board.caller.id-board.dealer.id-1)%4] # subtract one so that if caller-position here is 0, it's the dealer's left
    data += [2-int(board.called_first_round)]
    data += [int(board.going_alone)]
    data += [(w.id-board.dealer.id-1)%4 for w in board.winners]
    data += [board.points_this_round[(board.dealer.id+1)%2], board.points_this_round[board.dealer.id%2]]
    # now just write out the order of all the cards played -- string (card + player id) is fine
    # include the first word of the result as well ("EUCHRE", "Single", "Sweep", "Loner")
    # Total values after all this: 97 + 21 = 118

    # if dealer is 3, first trick is always 0 - 1 - 2 - 3
    # unless player 2 is going alone
    if board.going_alone and (board.caller.id + 1)%4 == board.dealer.id:
        data += [str(board.cards_played[i]) + str((i+1)%4) for i in range(4)]
    else:
        data += [str(board.cards_played[i]) + str(i) for i in range(4)]
    data += [str(board.cards_played[4*j+i]) + str((i+board.winners[j-1].id-board.dealer.id-1)%4) for j in range(1,5) for i in range(4)]
    #data += [board.result.split()[0]]
    data += ['Single' if 'single' in board.result.lower() else ('EUCHRE' if 'euchre' in board.result.lower() else ('Loner' if 'loner' in board.result.lower() else ('Sweep')))]
    data += [(i+board.dealer.id+1)%4 for i in range(4)]
    data += [board.caller.id] + [board.points_this_round[(board.caller.id)%2] - board.points_this_round[(board.caller.id+1)%2]]

    header = board.header
    if header == []:
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
        header += ['caller_trueid', 'caller_points']
    return data, header



THIS_IS_MY_HEADER = ['p0c1','p0c1isD','p0c1isH','p0c1isS','p0c2','p0c2isD','p0c2isH','p0c2isS','p0c3','p0c3isD','p0c3isH','p0c3isS',
'p0c4','p0c4isD','p0c4isH','p0c4isS','p0c5','p0c5isD','p0c5isH','p0c5isS','p1c1','p1c1isD','p1c1isH','p1c1isS','p1c2','p1c2isD','p1c2isH',
'p1c2isS','p1c3','p1c3isD','p1c3isH','p1c3isS','p1c4','p1c4isD','p1c4isH','p1c4isS','p1c5','p1c5isD','p1c5isH','p1c5isS','p2c1','p2c1isD',
'p2c1isH','p2c1isS','p2c2','p2c2isD','p2c2isH','p2c2isS','p2c3','p2c3isD','p2c3isH','p2c3isS','p2c4','p2c4isD','p2c4isH','p2c4isS','p2c5',
'p2c5isD','p2c5isH','p2c5isS','p3c1','p3c1isD','p3c1isH','p3c1isS','p3c2','p3c2isD','p3c2isH','p3c2isS','p3c3','p3c3isD','p3c3isH','p3c3isS',
'p3c4','p3c4isD','p3c4isH','p3c4isS','p3c5','p3c5isD','p3c5isH','p3c5isS','TC_power','TC_isD','TC_isH','TC_isS','trump_isD','trump_isH',
'trump_isS','caller','round','alone','winner1','winner2','winner3','winner4','winner5','points02','points13','played1','played2','played3',
'played4','played5','played6','played7','played8','played9','played10','played11','played12','played13','played14','played15','played16',
'played17','played18','played19','played20','result','p0trueid','p1trueid','p2trueid','p3trueid','caller_trueid','caller_points']

def suit_to_readable(arr):
    if len(arr) != 3: return None
    if arr[0]: return 'D'
    elif arr[1]: return 'H'
    elif arr[2]: return 'S'
    else: return 'C'
def power_to_readable(p):
    dkt = {1:'9', 2:'T', 3:'J', 4:'Q', 5:'K', 10:'A', 0:None, 12:'9', 15:'T', 20:'Q', 25:'K', 30:'A', 31:'J', 35:'J'}
    dkt.update({str(power):name for power,name in dkt.items()})
    return dkt[p]

def data_to_readable(gameline, header=[]):
    try:
        if hasattr(gameline[0], '__len__'): return [data_to_readable(l, header) for l in gameline]
    except:
        print(gameline)
        print(header)
        raise
    
    if len(header) == 0: header = THIS_IS_MY_HEADER
    header = np.array(header)
    def ix_from_name(name):
        all_ixs = np.where(header==name)[0]
        if len(all_ixs) == 0: raise ValueError(f'Name "{name}" not found in header "{header}"')
        return int(all_ixs)
    
    # A method to convert from "practical position" (dealer=3) to "true position" (deal passes around)
    convert_to_true = {i:gameline[ix_from_name(f'p{i}trueid')] for i in range(4)}
    
    # First get the trump suit
    trumpsuit = suit_to_readable(gameline[ix_from_name('trump_isD'):ix_from_name('trump_isD')+3])
    
    # Next get all of each players' cards
    player_cards = {i:[] for i in range(4)}
    for player in range(4):
        for card in range(5):
            card_here = f'p{player}c{card+1}'
            power = gameline[ix_from_name(card_here)]
            suit = gameline[ix_from_name(card_here+'isD'):ix_from_name(card_here+'isD')+3]
            player_cards[player].append(power_to_readable(power)+suit_to_readable(suit))
    player_cards = {convert_to_true[i]:player_cards[i] for i in range(4)} # convert from "practical" to "true" position
    
    # Get the rest of the global stuff
    caller_id = convert_to_true[gameline[ix_from_name('caller')]] # convert from "practical" to "true" position
    dealer_id = convert_to_true[3] # This is defined by the writing of the data -- convert from "practical" to "true" position
    called_first_round = gameline[ix_from_name('round')] == 1
    tc_power = gameline[ix_from_name('TC_power')]
    tc_suit = gameline[ix_from_name('TC_isD'):ix_from_name('TC_isD')+3]
    tc = power_to_readable(tc_power) + suit_to_readable(tc_suit)
    global_stuff = [trumpsuit, caller_id, dealer_id, called_first_round, tc]
    
    
    # Finally, get the played order of the cards, with winning card and winning ID noted
    start = ix_from_name('played1')
    tricks = {i:(gameline[start+(4*i) : start+4*(i+1)], gameline[ix_from_name(f'winner{i+1}')]) for i in range(5)}
    tricks = {k:([v[0][i][:-1] for i in range(4)], v[1]) for k,v in tricks.items()} # splice off player_id from card
    tricks = {k:(v[0], convert_to_true[v[1]]) for k,v in tricks.items()} # convert from "practical" to "true" position
    
    """
    What does desired output look like?
    {hands}, [globalstuff], {tricks}
    
    
    {
        '0': [9H, 10H, JH, AH, JD],
        ...
    },
    [TrumpSuit, CallerID, DealerID, FirstRound, TurnCard]
    {
        '0': ([AH*, KH, QH, 10H], 0)
        '1': ([9H, 9C, JS*, 10C], 2)
        ...
    }
    
    """
    return player_cards, global_stuff, tricks