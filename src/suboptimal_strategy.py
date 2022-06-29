from rule import Rule
from player import Player
import optimal_strategy as opt
# rule init: rule(condition, rule_type, name)
# condition: condition(board, player)

###################
# Basic player -- very simple strategy
###################

def make_BASIC_player(id):
    player = Player(
        id=id,
        hand=[],
        
        # from optimal strategy
        call_first_round_rules=opt.get_call_first_round_rules(),
        call_second_round_rules=opt.get_call_second_round_rules(),
        
        # created here
        lead_rules=get_leading_rules_BASIC(),
        lead_alone_rules=get_leading_alone_rules_BASIC(),
        follow_rules=get_follow_rules_BASIC(),
        
        first_round_threshold=opt.first_round_threshold,
        second_round_threshold=opt.second_round_threshold,
        going_alone_threshold=opt.going_alone_threshold
    )
    return player

def get_leading_rules_BASIC():
    rules = [
        Rule(opt.highest_remaining_trump, 'lead', 'highest remaining trump'),
        Rule(opt.offsuit_ace,             'lead', 'offsuit ace'),
        Rule(opt.best_off_card,           'lead', 'best off card'),
        Rule(opt.best_card,               'lead', 'best card')
    ]

    return rules

def get_leading_alone_rules_BASIC():
    rules = [
        Rule(opt.best_card,               'lead', 'best card')
    ]
    return rules

def get_follow_rules_BASIC():
    return [Rule(follow_BASIC, 'follow', 'basic follow')]

def follow_BASIC(board, player):
    
    # come back to this
    if board.going_alone:
        pass

    teamwinner, legal, winning_card, led_card, have_highest_trump, followsuit, have_trump, ntricks_team, ntricks_remaining = opt._current_state(board, player)
    n, c2_above, c3_above = opt._trump_spot_winning_card(board, player, teamwinner, winning_card)

    can_win, highest, lowest, lowest_winning = opt._key_cards(board, player, legal)
    lowest = min(legal, key=lambda x: x.power)

    if not can_win:                                                return(lowest)
    if not teamwinner:
        if led_card.trump:                                        return(lowest_winning)
        elif highest.suit == led_card.suit:                        return(highest)
        else:                                                    return(lowest_winning)
    
    # If you can't win the trick, play your lowest legal card
    
    # If your teammate **doesn't** have it:
        # If trump was led                                :    lowest winning
        # If you're following an off-suit                  :    highest
        # If you're trumping an off-suit                  :    lowest winning
    
    else:
        # If your teammate **does** have it:
        # let them take it
        return lowest
    
###################
# Intermediate Player -- healthy amount of strategy
###################
def make_INTERMEDIATE_player(id):
    player = Player(
        id=id,
        hand=[],
        
        # from optimal strategy
        call_first_round_rules=opt.get_call_first_round_rules(),
        call_second_round_rules=opt.get_call_second_round_rules(),
        
        # created here
        lead_rules=get_leading_rules_INTERMEDIATE(),
        lead_alone_rules=get_leading_alone_rules_INTERMEDIATE(),
        follow_rules=get_follow_rules_INTERMEDIATE(),
        
        # compare to optimal_strategy -- consider taking this out, since it might just dominate the results
        #first_round_threshold=1.1*first_round_threshold,
        #second_round_threshold=1.1*second_round_threshold,
        #going_alone_threshold=going_alone_threshold
        first_round_threshold=opt.first_round_threshold,
        second_round_threshold=opt.second_round_threshold,
        going_alone_threshold=opt.going_alone_threshold
    )
    return player

def get_leading_rules_INTERMEDIATE():
    # consider taking out one of the middle two
    rules = [
        Rule(opt.highest_remaining_trump, 'lead', 'highest remaining trump'),
        Rule(opt.offsuit_ace,             'lead', 'offsuit ace'),
        Rule(opt.caller_awkward_spot,     'lead', 'caller awkward spot'),
        Rule(opt.partners_jack,           'lead', 'partner\'s jack'),
        Rule(opt.mostly_trump,            'lead', 'mostly trump'),
        Rule(opt.best_off_card,           'lead', 'best off card')
    ]

    return rules

# keep this one the same
def get_leading_alone_rules_INTERMEDIATE():
    return get_leading_alone_rules_BASIC()

def get_follow_rules_INTERMEDIATE():
    return [Rule(follow_INTERMEDIATE, 'follow', 'intermediate follow')]

def follow_INTERMEDIATE(board, player):
        
    # come back to this
    if board.going_alone:
        pass

    teamwinner, legal, winning_card, led_card, have_highest_trump, followsuit, have_trump, ntricks_team, ntricks_remaining = opt._current_state(board, player)
    n, c2_above, c3_above = opt._trump_spot_winning_card(board, player, teamwinner, winning_card)

    can_win, highest, lowest, lowest_winning = opt._key_cards(board, player, legal)

    if not can_win:                                                return(lowest)
    if not teamwinner:
        if led_card.trump:
            if board.caller.id == player.id:                    return(highest)
            else:                                               return(lowest_winning)
        elif highest.suit == led_card.suit:                        return(highest)
        else:                                                    return(lowest_winning)
    
    # If you can't win the trick, play your lowest legal card
    
    # If your teammate **doesn't** have it:
        # If trump was led:
            # If you called trump                       :   highest
            # If you did not call trump                 :    lowest winning
        # If you're following an off-suit                  :    highest
        # If you're trumping an off-suit                  :    lowest winning
    
    else:
        if len(board.tricks[board.tnum-1]) == 3:                return(lowest)
        if led_card.trump:
            if have_highest_trump:                                return(highest)
            else:                                                return(lowest)
                
    # If your teammate **does** have it:
        # If you're the last person                                  :    lowest
        # If trump was led:
            # If you have the top card                            :    highest
            # If you don't have the top card                    :    lowest
        
        else:
            if winning_card.name == 'A':                            return(lowest)
            else:
                if followsuit:                                        return(highest)
                else:                                                return(lowest)
            
        # If an off-suit was led:
            # If your partner is     winning it with an ace        :    lowest
            # If your partner is not winning it with an ace:
                # If you have to follow suit            :    highest
                # If you don't have to follow suit        :    lowest