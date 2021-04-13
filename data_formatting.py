import numpy as np
from tqdm import notebook

COLS_GROUP1 = 24
COLS_GROUP2 = 47
COLS_GROUP3 = 24*13
COLS_GROUP4 = 55
COLS_TOTAL = COLS_GROUP1 + COLS_GROUP2 + COLS_GROUP3 + COLS_GROUP4
same_color_suit = {'C':'S', 'D':'H', 'H':'D', 'S':'C'}
def format_data(data, usetqdm=True, start=0, stop=None, count=None):
    """
    Here is all the data that needs to be fed to the ML algorithm, grouped by phase of the game.
    I have also tried to include an estimate of how many columns each will need to take up.
    If a categorical feature has N options, I will OHE it as N columns, instead of using N-1.
    A card will be OHEncoded as [9-A] + [C/D/H/S] (6+4), and possibly tagged as Y/N trump.
    
    #######
    DATA GROUP 1: Calling trump
    #######
    (4)  1.) Who dealt (position relative to "me")
    (4)  2.) Who called trump (position relative to "me")
    (1)  3.) Which round was trump called in
    (1)  4.) Going alone?
    (4)  5.) Which suit is trump (not sure about this one)
    (10) 6.) What is the turn card
    Total: 24 columns
    
    #######
    DATA GROUP 2: Other misc. information
    #######
    (4)  1.) Who is leading right now
    (4)  2.) Who is winning right now
    (11) 3.) What card was led (is it trump)
    (11) 4.) What card is winning (is it trump)
    (5)  5.) Which team won each trick so far (+1 for "me", 0 for no one (yet), -1 for opponents)
    (12) 6.) Any players confirmed short in any suits
    Total: 47 columns
    
    #######
    DATA GROUP 3: All card locations (constant order: 9C, 10C, ..., (D), (H), ..., KS, AS)
    #######
    For each card (24):
    (4)  1.) Confirmed in anyone's hand (my hand + ordered up turn card?)
    (4)  2.) Played in a previous trick by someone (maybe later expand this to which prev trick?)
    (3)  3.) Played in CURRENT trick by someone
    (1)  4.) Is trump
    Total: 288 columns
    
    #######
    DATA GROUP 4: My remaining hand, again
    #######
    (11) 1.) Card #1 (is it trump)
    (11) 2.) Card #2 (is it trump)
    (11) 3.) Card #3 (is it trump)
    (11) 4.) Card #4 (is it trump)
    (11) 5.) Card #5 (is it trump)
    Total: 55 columns
    
    SUPER-TOTAL: 414 columns. Yeesh.
    """
    
    counter = 0
    stop = len(data) if stop is None else stop
    count = len(data) if count is None else count
    formatted = np.zeros((20*(stop-start), COLS_TOTAL), dtype=np.int8)
    target = np.zeros((20*(stop-start), 24), dtype=np.int8)
    
    for i in notebook.tqdm(data.index) if usetqdm else data.index:
        i = int(i)
        if i < start:  continue
        elif i >= stop: break
        elif counter >= count: break
        
        game = data.iloc[i]
        formatted[20*counter:20*(counter+1)] = format_game(game)
        target[20*counter:20*(counter+1)] = get_target(game)
        counter += 1
    mask = ~np.all(target==0, axis=1)
    return formatted[mask], target[mask]

def format_game(game):
    formatted_game = np.zeros((20, COLS_TOTAL), dtype=np.int8)
    
    for tricknum in range(5):
        for playernum in range(4):
            if game['alone'] and int(game['caller'])==(int(get_current_player(game, tricknum, playernum))+2)%4:
                continue
            
            group1_info = get_group1_info(game, tricknum, playernum)
            group2_info = get_group2_info(game, tricknum, playernum)
            group3_info = get_group3_info(game, tricknum, playernum)
            group4_info = get_group4_info(game, tricknum, playernum)
            
            formatted_game[4*tricknum+playernum, :len(group1_info)] = group1_info
            formatted_game[4*tricknum+playernum, len(group1_info):len(group1_info)+len(group2_info)] = group2_info
            formatted_game[4*tricknum+playernum, len(group1_info)+len(group2_info):\
                           len(group1_info)+len(group2_info)+len(group3_info)] = group3_info
            formatted_game[4*tricknum+playernum, len(group1_info)+len(group2_info)+len(group3_info):\
                           len(group1_info)+len(group2_info)+len(group3_info)+len(group4_info)] = group4_info
    return formatted_game

def get_group1_info(game, tricknum, playernum):
    """
    #######
    DATA GROUP 1: Calling trump
    #######
    (4)  1.) Who dealt (position relative to "me")
    (4)  2.) Who called trump (position relative to "me")
    (1)  3.) Which round was trump called in
    (1)  4.) Going alone?
    (4)  5.) Which suit is trump (not sure if this one needs to be here)
    (10) 6.) What is the turn card
    Total: 24 columns
    """
    group1_info = np.zeros(COLS_GROUP1, dtype=np.int8)
    current_player = get_current_player(game, tricknum, playernum)
    
    # who dealt
    group1_info[get_relative_position(game, tricknum, playernum, '3')] = 1
    # who called
    group1_info[4+get_relative_position(game, tricknum, playernum, game['caller'])] = 1
    # was it called first round
    group1_info[8] = 2-int(game['round'])
    # did they go alone
    group1_info[9] = int(game['alone'])
    # which suit is trump
    group1_info[10+{'C':0, 'D':1, 'H':2, 'S':3}[get_trump_suit(game)]] = 1
    # what is the turn card
    turn_card = get_turn_card(game)
    group1_info[14+{n:i for n,i in zip(list('9TJQKA'), range(6))}[turn_card[0]]] = 1
    group1_info[20+{s:i for s,i in zip(list('CDHS'), range(4))}[turn_card[1]]] = 1
    
    return group1_info

def get_group2_info(game, tricknum, playernum):
    """
    #######
    DATA GROUP 2: Other misc. information
    #######
    (4)  1.) Who is leading right now
    (4)  2.) Who is winning right now
    (11) 3.) What card was led (is it trump)
    (11) 4.) What card is winning (is it trump)
    (5)  5.) Which team won each trick so far (+1 for "me", 0 for no one (yet), -1 for opponents)
    (12) 6.) Any players confirmed short in any suits
    Total: 47 columns
    """
    group2_info = np.zeros(COLS_GROUP2, dtype=np.int8)
    current_trick = game[['played'+str(i+1) for i in range(4*tricknum, 4*tricknum+playernum)]]
    trump_suit = get_trump_suit(game)
    
    # who leads
    group2_info[get_relative_position(game, tricknum, playernum, current_trick[0][-1]) if len(current_trick) > 0 else 3] = 1
    # who's winning
    if len(current_trick) > 0:
        winner, winning_card = get_winner(current_trick, trump_suit)
        group2_info[4+get_relative_position(game, tricknum, playernum, winner)] = 1
    # what card was led
    if len(current_trick) > 0:
        group2_info[8+{n:i for n,i in zip(list('9TJQKA'), range(6))}[current_trick[0][0]]] = 1
        group2_info[14+{s:i for s,i in zip(list('CDHS'), range(4))}[current_trick[0][1]]] = 1
        group2_info[18] = (current_trick[0][1]==trump_suit) or (current_trick[0][0]=='J' and current_trick[0][1]==same_color_suit[trump_suit])
    # what card is winning
    if len(current_trick) > 0:
        group2_info[19+{n:i for n,i in zip(list('9TJQKA'), range(6))}[winning_card[0]]] = 1
        group2_info[25+{s:i for s,i in zip(list('CDHS'), range(4))}[winning_card[1]]] = 1
        group2_info[29] = (winning_card[1]==trump_suit) or (winning_card[0]=='J' and winning_card[1]==same_color_suit[trump_suit])
    # what team won each trick so far
    for tnum in range(5):
        if tnum >= tricknum:
            continue
        # return +1 if relative_position % 2 == 1, return -1 if relative_position % 2 == 0 (self is always 3)
        group2_info[30+tnum] = -1+2*(get_relative_position(game, tricknum, playernum, game['winner'+str(tnum+1)])%2)
    # any players confirmed short in suits
    # list it like [opp1 short in clubs, opp1 short in diamonds, ..., opp2 short in spades]
    for opp_pos in range(3):
        for i, s in enumerate(list('CDHS')):
            group2_info[35+4*opp_pos + i] = get_short_suitedness(game, tricknum, playernum, opp_pos, s)

    return group2_info

card_ix = {**{n:i for n,i in zip(list('9TJQKA'), range(6))},\
            **{s:6*i for s,i in zip(list('CDHS'), range(4))}}
def get_group3_info(game, tricknum, playernum):
    """
    #######
    DATA GROUP 3: All card locations (constant order: 9C, 10C, ..., (D), (H), ..., KS, AS)
    #######
    For each card (24):
    (4)  1.) Confirmed in anyone's hand (my hand + ordered up turn card?)
    (4)  2.) Played in a previous trick by someone (maybe later expand this to which prev trick?)
    (3)  3.) Played in CURRENT trick by someone
    (1)  4.) Confirmed buried
    (1)  5.) Is trump
    Total: 312 columns
    """
    COLS_PER_CARD = 13
    group3_info = np.zeros(24*COLS_PER_CARD, dtype=np.int8)
    trump_suit = get_trump_suit(game)
    
    # cards played in a previous trick
    if tricknum > 0:
        prev_played_cards = game[['played'+str(i+1) for i in range(4*tricknum)]]
        for c in prev_played_cards:
            if '-' in c:
                continue
            group3_info[COLS_PER_CARD*(card_ix[c[0]] + card_ix[c[1]]) + 4 + get_relative_position(game, tricknum, playernum, c[-1])] = 1
    
    # cards played THIS trick
    if playernum > 0:
        current_played_cards = game[['played'+str(i+1) for i in range(4*tricknum, 4*tricknum+playernum)]]
        for c in current_played_cards:
            if c.startswith('-'):
                continue
            group3_info[COLS_PER_CARD*(card_ix[c[0]] + card_ix[c[1]]) + 8 + get_relative_position(game, tricknum, playernum, c[-1])] = 1
    
    # cards in my hand
    my_remaining_cards = [c[:-1] for c in game[['played'+str(i+1) for i in range(4*tricknum+playernum, 20)]]\
                    if c[-1] == get_current_player(game, tricknum, playernum)]
    for c in my_remaining_cards:
        # position of self wrt self is always 3
        group3_info[COLS_PER_CARD*(card_ix[c[0]] + card_ix[c[1]]) + 3] = 1
        
    # confirmed turn card location
    if game['round']==2:
        turn_card = get_turn_card(game)
        group3_info[COLS_PER_CARD*(card_ix[turn_card[0]] + card_ix[turn_card[1]]) + COLS_PER_CARD-2] = 1
    elif get_current_player(game, tricknum, playernum) == '3':
        original_cards = get_original_hand(game, tricknum, playernum)
        played_cards = [c[:-1] for c in game[['played'+str(i+1) for i in range(20)]] if c[-1]=='3']
        buried_card = [c for c in original_cards if c not in played_cards][0]
        group3_info[COLS_PER_CARD*(card_ix[buried_card[0]]+card_ix[buried_card[1]]) + COLS_PER_CARD-2] = 1
    else:
        turn_card = get_turn_card(game)
        all_played_cards = game[['played'+str(i+1) for i in range(4*tricknum+playernum)]]
        if turn_card+'3' not in list(all_played_cards):
            group3_info[COLS_PER_CARD*(card_ix[turn_card[0]]+card_ix[turn_card[1]]) + get_relative_position(game, tricknum, playernum, 3)] = 1
    
    # Mark trump
    for s in list('CDHS'):
        if s == trump_suit:
            for name in list('9TJQKA'):
                group3_info[COLS_PER_CARD*(card_ix[name]+card_ix[s]) + COLS_PER_CARD-1] = 1
            group3_info[COLS_PER_CARD*(card_ix['J']+card_ix[same_color_suit[s]]) + COLS_PER_CARD-1] = 1
        
    return group3_info

def get_group4_info(game, tricknum, playernum):
    """
    #######
    DATA GROUP 4: My remaining hand, again
    #######
    (11) 1.) Card #1 (is it trump)
    (11) 2.) Card #2 (is it trump)
    (11) 3.) Card #3 (is it trump)
    (11) 4.) Card #4 (is it trump)
    (11) 5.) Card #5 (is it trump)
    Total: 55 columns
    """
    """
    my_cards = [c for c in game[['played'+str(i) for i in range(1,21)]] if c[-1] == str(playernum)]
    trump_suit = get_trump_suit(game)
    np.random.shuffle(my_cards)
    my_cards = [c[:-1] if c not in game[['played'+str(i) for i in range(1,4*tricknum+playernum+1)]] else '00' for c in my_cards]
    """
    # slightly more efficient
    trump_suit = get_trump_suit(game)
    my_cards = [c[:-1] for c in game[['played'+str(i+1) for i in range(4*tricknum+playernum, 20)]]\
                if c[-1] == get_current_player(game, tricknum, playernum)]
    my_cards += ['00']*(5-len(my_cards))
    np.random.shuffle(my_cards)
    
    group4_info = []
    for c in my_cards:
        group4_info += card_to_ohe(c[0], c[1], trump_suit==c[1] or (c[0]=='J' and c[1]==same_color_suit[trump_suit]))
    return group4_info

def get_winner(current_trick, trump_suit):
    winning_card = current_trick[0]
    powers = {n+s:p for n,p in zip(list('9TJQKA'), [1,2,3,4,5,10]) for s in list('CDHS') if s != trump_suit}
    powers['J'+same_color_suit[trump_suit]] = 31
    powers.update({n+trump_suit:p for n,p in zip(list('9TQKAJ'), [12,15,20,25,30,35])})
    
    for i in range(1,len(current_trick)):
        c = current_trick[i]
        if c.startswith('-'):
            continue
        # if winning card is trump, just compare powers
        if winning_card[1] == trump_suit or (winning_card[0]=='J' and winning_card[1]==same_color_suit[trump_suit]):
            if powers[c[:2]] > powers[winning_card[:2]]:
                winning_card = c
        else:
            # first, check if card is trump
            if powers[c[:2]] > 10:
                winning_card = c
            # next, check if some random offsuit
            elif c[1] != winning_card[1]:
                continue
            # by now, determined neither are trump, and both have the same suit
            else:
                if powers[c[:2]] > powers[winning_card[:2]]:
                    winning_card = c
    return int(winning_card[-1]), winning_card[:2]

def get_short_suitedness(game, tricknum, playernum, opp_pos, short_suit):
    led_cards = [c for c in game[['played'+str(i+1) for i in range(4*tricknum+playernum)]][::4]]
    trump_suit = get_trump_suit(game)
    
    for i, c in enumerate(led_cards):
        # skip if they lead
        if get_relative_position(game, tricknum, playernum, c[-1]) == opp_pos:
            continue
        
        # checking against a specific suit, so make sure the led suit is that suit
        # (or else if we're checking against trump and the left is led)
        if c[1] != short_suit or (c[0]=='J' and c[1]==same_color_suit[trump_suit] and short_suit==same_color_suit[trump_suit]):
            continue
        
        associated_trick = game[['played'+str(ix+1) for ix in range(4*i, min(4*(i+1), 4*tricknum+playernum))]]
        # skip if they haven't played yet
        if opp_pos not in [get_relative_position(game, tricknum, playernum, c[-1]) for c in associated_trick]:
            continue
        opp_played_card = [c for c in associated_trick if get_relative_position(game, tricknum, playernum, c[-1])==opp_pos][0]
        
        if c[1] == trump_suit or (c[0]=='J' and c[1] == same_color_suit[trump_suit]):
            # "if not trump suit and also is not left"
            if opp_played_card[1] != trump_suit and not (opp_played_card[0]=='J' and opp_played_card[1]==same_color_suit[trump_suit]):
                return 1
        else:
            # "if not same suit or is left"
            if opp_played_card[1] != c[1] or (opp_played_card[0]=='J' and opp_played_card[1]==same_color_suit[trump_suit]):
                return 1
    return 0

def get_current_player(game, tricknum, playernum):
    return game['played'+str(4*tricknum+playernum+1)][-1]

def get_relative_position(game, tricknum, playernum, pos):
    return (int(pos) - int(get_current_player(game, tricknum, playernum)) - 1)%4
    # self maps to 3, then advances positively by advancing other player pos
    
power_to_name = {power:n for power,n in zip([1,2,3,4,5,10,12,15,20,25,30,31,35], list('9TJQKA9TQKAJJ'))}
def get_turn_card(game):
    name = power_to_name[game['TC_power']]
    if game['TC_isD']: return name+'D'
    elif game['TC_isH']: return name+'H'
    elif game['TC_isS']: return name+'S'
    else: return name+'C'
    
oldstyle=False
def get_original_hand(game, tricknum, playernum):
    player = get_current_player(game, tricknum, playernum)
    if oldstyle: player = (int(player)+1)%4
    return [power_to_name[game['p'+str(player)+'c'+str(i+1)]] + 
            'D'*game['p'+str(player)+'c'+str(i+1)+'isD'] + \
            'H'*game['p'+str(player)+'c'+str(i+1)+'isH'] + \
            'S'*game['p'+str(player)+'c'+str(i+1)+'isS'] + \
                'C'*(1-game['p'+str(player)+'c'+str(i+1)+'isD']-\
                     game['p'+str(player)+'c'+str(i+1)+'isH']-\
                     game['p'+str(player)+'c'+str(i+1)+'isS'])\
            for i in range(5)]

def get_trump_suit(game):
    if game['trump_isD']: return 'D'
    elif game['trump_isH']: return 'H'
    elif game['trump_isS']: return 'S'
    else: return 'C'
    
def card_to_ohe(name, suit, trump=None):
    arr = [0]*10
    for i, n in enumerate(['9', 'T', 'J', 'Q', 'K', 'A']):
        if name == n:
            arr[i] = 1
            break
    for i, s in enumerate(['C', 'D', 'H', 'S']):
        if suit == s:
            arr[6+i] = 1
            break
    if trump is not None:
        arr += [int(trump)]
    return arr

card_ix = {**{n:i for n,i in zip(list('9TJQKA'), range(6))},\
            **{s:6*i for s,i in zip(list('CDHS'), range(4))}}
def get_target(game):
    target = np.zeros((20, 24), dtype=np.int8)
    for i, c in enumerate(game[['played'+str(ix+1) for ix in range(20)]]):
        if '-' in c:
            continue
        target[i][card_ix[c[0]] + card_ix[c[1]]] = 1
    return target