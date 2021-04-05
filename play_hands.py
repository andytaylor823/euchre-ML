from board import Board
from euchre_lib import *
import sys
import os
from tqdm import tqdm

"""
Accepted flags:

--t:        p0 and p2 threshold
--o:        p1 and p3 threshold
--root:     path to root directory
--ne:       number of epochs
--nh:       number of hands per epoch
--rmdir:    0/1 whether to remove an existing output dir or not -- default to not
--tqdm:     0/1 whether or not to use tqdm -- default to not
--id:       position for the tqdm progress bar -- default will fail if usetqdm is true and this is not set
"""

flags = (''.join(sys.argv)).split('--')[1:]
opts = {}
try:
    for f in flags:
        if f[:6] == 'thresh':
            opts['thresh'] = int(f[6:])
        elif f[0] == 'o':
            opts['oppthresh'] = int(f[1:])
        elif f[:4] == 'root':
            opts['rootpath'] = f[4:]
        elif f[:2] == 'ne':
            opts['n_epochs'] = int(f[2:])
        elif f[:2] == 'nh':
            opts['n_hands'] = int(f[2:])
        elif f[:5] == 'rmdir':
            opts['rmdir'] = int(f[5:])
        elif f[:4] == 'tqdm':
            opts['tqdm'] = int(f[4:])
        elif f[:2] == 'id':
            opts['id'] = int(f[2:])
        else:
            pass
    if opts.get('tqdm') and not opts.get('id'):
        raise ValueError

except:
    print('ERROR WITH THE INPUTS')
    print(opts)
    print(flags)
    exit(10)
    
p0 = make_conservative_player(0, opts['thresh']) if 'thresh' in opts else None
p1 = make_conservative_player(1, opts['oppthresh']) if 'oppthresh' in opts else None
p2 = make_conservative_player(2, opts['thresh']) if 'thresh' in opts else None
p3 = make_conservative_player(3, opts['oppthresh']) if 'oppthresh' in opts else None

thresh = opts['thresh'] if 'thresh' in opts else 70
folder = 'thresh' + str(thresh)
root = opts['rootpath'] if 'rootpath' in opts else os.getcwd()
if folder in os.listdir(root):
    if opts.get('rmdir'):
        os.system('rm -r ' + str(os.path.join(root, folder)))
if not os.path.isdir(os.path.join(root, folder)):
    os.mkdir(os.path.join(root, folder))
outpath = os.path.join(root, folder)

n_epochs = opts['n_epochs'] if 'n_epochs' in opts else 10
n_hands = opts['n_hands'] if 'n_hands' in opts else 100

t_est = n_epochs*n_hands/500 # estimate 500 hands per sec
if t_est < 180:
    print('Estimated time: %.2f seconds' %t_est)
elif t_est < 60*180:
    print('Estimated time: %.2f minutes' %(t_est/60))
else:
    print('Estimated time: %.2f hours' %(t_est/3600))

board = Board(p0, p1, p2, p3)

iterable = tqdm(range(n_epochs), position=opts['id'], desc='Threshold '+str(thresh)) if opts.get('tqdm') else range(n_epochs)
for epoch in iterable:
    for _ in range(n_hands):
        board.play_hand()
    board.writeout(folder=outpath, keep_results=False, ROOT_DIR=root)

print('Done with thresh %i' %thresh)

