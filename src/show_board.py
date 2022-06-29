def show(board, asvar=False):
    if not board.show:
        return

    if board.result is not None:
        lines = ['Hand is finished!']
        lines.append(board.result)
        lines.append('Players 0/2 score: %i (%i tricks)\nPlayers 1/3 score: %i (%i tricks)' \
            %(board.points[0], board.ntricks[0]+board.ntricks[2], board.points[1], board.ntricks[1]+board.ntricks[3]))
        print('\n'.join(lines))

        if asvar: return lines
        else:     return None
    print('result:', board.result)

    p3 = board.dealer
    p0 = board.players[board._next_pos(p3.id)]
    p1 = board.players[board._next_pos(p0.id)]
    p2 = board.players[board._next_pos(p1.id)]

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
            if len(p1.hand) < 6-board.tnum:
                s += zerohand_to_onethree_cardplayed_space + str(board.current_trick[(p1.id-board.leader.id)%4]) + zerohand_to_onethree_cardplayed_space # mirror
            else:
                s += zerohand_to_onethreehand_space + onethreehand_placeholder_space + onethreehand_to_twohand_space

        elif i == 2:
            if len(p0.hand) < 6-board.tnum:
                s += zerohand_to_zero_cardplayed_space + str(board.current_trick[(p0.id-board.leader.id)%4])
                if len(p2.hand) < 6-board.tnum:
                    s += zero_cardplayed_to_two_cardplayed_space + str(board.current_trick[(p2.id-board.leader.id)%4]) + zerohand_to_zero_cardplayed_space # mirror
                else:
                    s += zero_cardplayed_to_twohand_space
            elif len(p2.hand) < 6-board.tnum:
                s += zerohand_to_two_cardplayed_space + str(board.current_trick[(p2.id-board.leader.id)%4]) + zerohand_to_zero_cardplayed_space # mirror
            else:
                s += zerohand_to_onethreehand_space + onethreehand_placeholder_space + onethreehand_to_twohand_space

        elif i == 3:
            if len(p3.hand) < 6-board.tnum:
                s += zerohand_to_onethree_cardplayed_space + str(board.current_trick[(p3.id-board.leader.id)%4]) + zerohand_to_onethree_cardplayed_space # mirror
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
    lines.append('Turn card: ' + str(board.turn_card) + ', Player %i is dealer' %board.dealer.id)
    if board.trump_suit is not None:
        lines.append('Trump suit: *' + str(full_names[board.trump_suit]).upper() + '* (called %s round by Player %i)'\
                 %('first' if board.called_first_round else 'second', board.caller.id))
    if board.going_alone:
        lines.append('THIS PLAYER IS GOING ALONE')

    if len(board.cards_played) > 0:
        lines.append('')
        lines.append('Player %i led, and Player %i is winning' %(board.leader.id, board.winner.id))

    lines.append('Players 0/2 score: %i (%i tricks currently)\nPlayers 1/3 score: %i (%i tricks currently)' \
            %(board.points[0], board.ntricks[0]+board.ntricks[2], board.points[1], board.ntricks[1]+board.ntricks[3]))

    # final line break to close it out
    lines.append('\n')


    print('\n'.join(lines))
    x = ''
    while x.lower() not in ['x', 'c']:
        x = input('Enter "c" to continue, "x" to exit: ')

    if x.lower() == 'x':
        if board.in_kernel:
            sys.exit()
        else:
            exit()
    if asvar:
        return lines