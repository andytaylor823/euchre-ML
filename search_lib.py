import numpy as np
import os
from card import Card
from board import Board
from player import Player
from rule import Rule
import optimal_strategy as opt

import pandas as pd
pd.set_option('display.max_columns', 200)

import multiprocessing
import time
from tqdm import notebook
notebook.tqdm.pandas()

from euchre_lib import *


def caller_trueid(row):
    return row['p' + str(row['caller']) + 'trueid']

def search_performance(thresholds, n_epochs=10, n_hands=1000, opp_thresh=None, prnt=True, folder=None):

    folder = 'aggressive' if folder is None else folder
    if not hasattr(thresholds, '__len__'):
        thresholds = [thresholds]
    performance, std = [], []
    # will run (55, 0) + (55, 1) + (55, 2) + ... + (55, 9) + (60, 0) + ... + (100, 9)
    iterable = [(t, epoch) for t in thresholds for epoch in range(n_epochs)]
    
    # do this for 3 cases next
    for t, epoch in notebook.tqdm(iterable):
        if epoch == 0:
            if folder in os.listdir():
                os.system('rm -r ' + folder)
        p0 = make_conservative_player(0, t)
        p2 = make_conservative_player(2, t)
        if opp_thresh is not None:
            p1 = make_conservative_player(1, opp_thresh)
            p3 = make_conservative_player(3, opp_thresh)
            board = Board(p0=p0, p1=p1, p2=p2, p3=p3)
        else:
            board = Board(p0=p0, p2=p2)

        for hand in range(n_hands):
            board.play_hand()
        board.writeout(folder=folder, keep_results=False)

        if epoch == n_epochs-1:
            if prnt:
                notebook.tqdm.write('Evaluating performance for threshold %i...' %t)
            df = read_all_hands(folder=folder+'/', use_tqdm=False)
            df['caller_trueid'] = df.apply(caller_trueid, axis=1)
            df['caller_points'] = df.apply(lambda x: 4*(x['result']=='Loner') + 2*(x['result']=='Sweep') + 1*(x['result']=='Single') - 2*(x['result']=='EUCHRE'), axis=1)
            calls = [df[df['caller_trueid']==i] for i in range(4)]
            points = [calls[i]['caller_points'].sum() for i in range(4)]

            performance.append(points[0]+points[2])
            std.append(np.sqrt(calls[0]['caller_points'].std()**2 + calls[2]['caller_points'].std()**2))
    print('Done!')
    return(np.array(performance), np.array(std))

def search_performance_parallel(thresholds, id, n_epochs=10, n_hands=1000, opp_thresh=None, folder=None, title=None, ROOT_DIR=os.getcwd()):
    print(' ', end='', flush=True)
    ROOT_DIR = ROOT_DIR + '/' if ROOT_DIR[-1] != '/' else ROOT_DIR
    
    if not hasattr(thresholds, '__len__'):
        thresholds = [thresholds]
    if title is None:
        if len(thresholds)==1:
            title = 'Threshold = ' + str(thresholds[0])
        else:
             title = 'Job #' + str(id)
    #progress = notebook.tqdm(total=n_epochs*len(thresholds), position=id, desc=title)
    
    
    folder = 'aggressive' if folder is None else folder
    folder = os.path.join(ROOT_DIR, folder)
    
    
    if not hasattr(thresholds, '__len__'):
        thresholds = [thresholds]
    performance, std = [], []
    # will run (55, 0) + (55, 1) + (55, 2) + ... + (55, 9) + (60, 0) + ... + (100, 9)
    iterable = [(t, epoch) for t in thresholds for epoch in range(int(n_epochs))]
    
    # do this for 3 cases next
    for t, epoch in notebook.tqdm(iterable, position=id, desc=title):
        if epoch == 0:
            if folder.split('/')[-1] in os.listdir(ROOT_DIR):
                os.system('rm -r ' + folder)
        p0 = make_conservative_player(0, t)
        p2 = make_conservative_player(2, t)
        if opp_thresh is not None:
            p1 = make_conservative_player(1, opp_thresh)
            p3 = make_conservative_player(3, opp_thresh)
            board = Board(p0=p0, p1=p1, p2=p2, p3=p3)
        else:
            board = Board(p0=p0, p2=p2)

        for hand in range(int(n_hands)):
            board.play_hand()
        board.writeout(folder=folder, keep_results=False, ROOT_DIR=ROOT_DIR)
        #progress.update(1)

    #progress.close()
    board = None
    

def parallel_search_wrapper(thresholds, MAX_CPUS=8, n_epochs=10, n_hands=100, opp_thresh=None,
                            title=None, ROOT_DIR=os.getcwd()+'/'):
    t1 = time.time()
    if ROOT_DIR[-1] == '/':
        if ROOT_DIR[:-1] not in os.listdir():
            os.mkdir(ROOT_DIR[:-1])
    else:
        if ROOT_DIR not in os.listdir():
            os.mkdir(ROOT_DIR)
    
    N_CPUS = min(MAX_CPUS, multiprocessing.cpu_count()-1)
    pool = multiprocessing.Pool(N_CPUS)
    for i in range(len(thresholds)):
        folder = 'thresh' + str(thresholds[i])
        pool.apply_async(search_performance_parallel, args=(thresholds[i], i, n_epochs, n_hands, opp_thresh, folder, title, ROOT_DIR))
    pool.close()
    pool.join()
    dt = time.time()-t1
    print('Done!')
    print('This took %.2f seconds' %dt)
    if dt > 5*60:
        print('This took %.2f minutes' %(dt/60))
    if dt > 3600*3:
        print('This took %.2f hours' %(dt/3600))

        
        
def get_performance_wrapped(path, outfile=None, amount_tqdm=2, use_mp=True, ROOT_DIR=os.getcwd()):
    if use_mp:
        print(' ', end='', flush=True)
    
    if os.path.isdir(path):
        thresh = int(path.split('thresh')[-1])
            
        if amount_tqdm > 0:
            notebook.tqdm.write('Threshold ' + str(thresh) + '...')
            
        df = read_all_hands(folder=path, use_tqdm = (amount_tqdm > 2))
        if amount_tqdm > 1:
            df['caller_trueid'] = df.progress_apply(caller_trueid, axis=1)
            df['caller_points'] = df.progress_apply(lambda x: 4*(x['result']=='Loner') + 2*(x['result']=='Sweep') + 1*(x['result']=='Single') - 2*(x['result']=='EUCHRE'), axis=1)
        elif amount_tqdm > 0:
            df['caller_trueid'] = df.apply(caller_trueid, axis=1)
            df['caller_points'] = df.progress_apply(lambda x: 4*(x['result']=='Loner') + 2*(x['result']=='Sweep') + 1*(x['result']=='Single') - 2*(x['result']=='EUCHRE'), axis=1)
        else:
            df['caller_trueid'] = df.apply(caller_trueid, axis=1)
            df['caller_points'] = df.apply(lambda x: 4*(x['result']=='Loner') + 2*(x['result']=='Sweep') + 1*(x['result']=='Single') - 2*(x['result']=='EUCHRE'), axis=1)
                
        calls = [df[df['caller_trueid']==i] for i in range(4)]
        points = [calls[i]['caller_points'].sum() for i in range(4)]

        tot_sum = points[0]+points[2]
        tot_std = np.sqrt(calls[0]['caller_points'].std()**2 + calls[2]['caller_points'].std()**2) * np.sqrt(len(df))
        opp_sum = points[1]+points[3]
        opp_std = np.sqrt(calls[1]['caller_points'].std()**2 + calls[3]['caller_points'].std()**2) * np.sqrt(len(df))
        
        
        outfile = 'performance.csv' if outfile is None else outfile
        #outfile = os.path.join(ROOT_DIR, outfile)
        with open(outfile, 'a') as f:
            f.write(','.join([str(v) for v in [thresh, tot_sum, tot_std, opp_sum, opp_std, len(df)]]) + '\n')
    
    
def get_performance(ROOT_DIR=os.getcwd()+'/', outfile=None, amount_tqdm=2, use_mp=True, MAX_CPUS=8): # options for "amount_tqdm" are 0, 1, 2, and 3+
    
    if outfile is None:
        if 'performance.csv' in os.listdir(ROOT_DIR):
            outfile = next(('performance'+str(i)+'.csv' for i in range(1,101) if 'performance'+str(i)+'.csv' not in os.listdir(ROOT_DIR)), 'performance100.csv')
        else:
            outfile = 'performance.csv'
    outfile = os.path.join(ROOT_DIR, outfile)
    print('Writing to file: %s' %outfile)
    with open(outfile, 'w') as f:
        f.write('Threshold,TotalSum,TotalStd,OppSum,OppStd,TotalHands\n')
    
    if use_mp:
        # load fewer things into memory?
        N_CPUS = min(multiprocessing.cpu_count()-1, MAX_CPUS)
        pool = multiprocessing.Pool(N_CPUS)
        print(' ', end='', flush=True) if amount_tqdm > 0 else None
    
    iterable = notebook.tqdm(os.listdir(ROOT_DIR)) if amount_tqdm > 0 and not use_mp else os.listdir(ROOT_DIR)
    for folder in iterable:
        path = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(path):
            continue
        try:
            thresh = int(path.split('thresh')[-1])
            if use_mp:
                pool.apply_async(get_performance_wrapped, args=(path, outfile, amount_tqdm, True, ROOT_DIR))
            else:
                get_performance_wrapped(path, outfile, amount_tqdm, False, ROOT_DIR)
            
        except:
            continue
            
    if use_mp:
        pool.close()
        pool.join()

    print('Done!')
            
    