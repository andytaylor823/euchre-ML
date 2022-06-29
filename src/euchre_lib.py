import os
import optimal_strategy as opt
import pandas as pd
from tqdm import notebook
from player import Player
notebook.tqdm.pandas()

def read_all_hands(folder='stored_runs/', use_tqdm=True):
    df = None            
    iterable = notebook.tqdm(os.listdir(folder)) if use_tqdm else os.listdir(folder)
    folder = folder + '/' if folder[-1] != '/' else folder
    
    final_df = pd.concat([pd.read_csv(folder+file) for file in iterable if '.csv' in file]).reset_index(drop=True)
    return(final_df)


def make_conservative_player(id, first=90, second=None):
    player = Player(
        id=id,
        hand=[],
        call_first_round_rules=opt.get_call_first_round_rules(),
        call_second_round_rules=opt.get_call_second_round_rules(),
        lead_rules=opt.get_leading_rules(),
        lead_alone_rules=opt.get_leading_alone_rules(),
        follow_rules=opt.get_follow_rules(),
        first_round_threshold=first,
        second_round_threshold=first if second is None else second
    )
    return(player)
