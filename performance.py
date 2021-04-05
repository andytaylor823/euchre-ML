import numpy as np 
import pandas as pd
import os
import sys
import multiprocessing
from search_lib import *

"""
Accepted flags:

--root:     path to root directory -- default cwd
--NCPUS:    amount of CPUs / cores / threads available for this job -- default 8
--outfile:  optional name of outfile
"""

flags = (''.join(sys.argv)).split('--')[1:]
opts = {}
try:
    for f in flags:
        if f[:4] == 'root':
            opts['rootpath'] = f[4:]
        elif f[:5].lower() == 'ncpus':
            opts['NCPUS'] = int(f[5:])
        elif f[:7] == 'outfile':
            opts['outfile'] = f[7:]
        else:
            pass 

except:
    print('ERROR WITH THE INPUTS')
    exit(10)
    pass

root = opts['rootpath'] if 'rootpath' in opts else os.getcwd()
N_CPUS = opts['NCPUS'] if 'NCPUS' in opts else 8
folders = [f for f in os.listdir(root) if os.path.isdir(os.path.join(root, f)) and '.ipyn' not in f]

pool = multiprocessing.Pool(N_CPUS)
get_performance(ROOT_DIR=root, outfile=opts.get('outfile'), amount_tqdm=0, MAX_CPUS=N_CPUS)
