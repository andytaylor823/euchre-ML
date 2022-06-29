import tensorflow as tf
tf.compat.v1.enable_eager_execution()
from tensorflow import keras
#print(tf.__version__)
import os
import numpy as np
from functools import partial

from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.metrics import AUC, Precision, Recall, CategoricalAccuracy
from tensorflow.keras import initializers, regularizers
from tensorflow.keras.callbacks import TensorBoard

import data_formatting as dtf
import format_to_tfrecord as ftt

BATCH_SIZE = 10
def make_model(dense_layers=None, drop_prob=0, reg=0, learning_rate=None):
    inputs = layers.Input(shape=(dtf.COLS_TOTAL,), batch_size=BATCH_SIZE)
    if dense_layers is None:
        dense_layers = [int(i/5*dtf.COLS_TOTAL) for i in range(20, 0, -3)]
    # option for N layers, starting with 4x the number of columns
    elif not hasattr(dense_layers, '__len__'):
        dense_layers = [int(i/5*dtf.COLS_TOTAL) for i in np.linspace(20, 0, dense_layers)]
    else:
        if max(dense_layers) < 10:
            dense_layers = [l*dtf.COLS_TOTAL for l in dense_layers]
            
    dense_layers = sorted([int(l) for l in dense_layers], reverse=True)
    
    x = None
    for dense_units in dense_layers:
        if x is None:
            x = layers.Dense(dense_units, kernel_regularizer=regularizers.l2(reg))(inputs)
        else:
            x = layers.Dense(dense_units, kernel_regularizer=regularizers.l2(reg))(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.Dropout(drop_prob)(x)
    
    outputs = layers.Dense(dtf.COLS_TARGET, activation='softmax')(x)
    opt = keras.optimizers.Adam(learning_rate=learning_rate) if learning_rate else keras.optimizers.Adam()
    metrics = [CategoricalAccuracy(), Precision(), Recall(), AUC()]
    #loss = keras.losses.SparseCategoricalCrossentropy()
    loss = keras.losses.CategoricalCrossentropy()
    
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=opt, loss=loss, metrics=metrics)
    
    return model

def get_dataset(filenames, singular_plays_keep_prob=0.1):
    dataset = None
    for file in filenames:
        if dataset is None:
            dataset = ftt.read_dataset(file)
        else:
            dataset = dataset.concatenate(ftt.read_dataset(file))
    
    # remove the specified fraction of singular plays
    dataset = dataset.map(
        lambda data,target: tf.py_func(partial(remove_singular_plays, keep_prob=singular_plays_keep_prob),\
        [data,target], [tf.int8, tf.int8]))
    
    # this line is critical, since each TFrecord dataset is just one object of size (200k, 438) + (200k, 24)
    dataset = dataset.unbatch()
    # now, batch it the way I want it to be batched
    dataset = dataset.batch(BATCH_SIZE)
    dataset = dataset.shuffle(10*BATCH_SIZE)
    dataset = dataset.prefetch(buffer_size=10*BATCH_SIZE)
    #dataset = dataset.repeat()
    dataset = dataset.map(lambda data,target: (tf.ensure_shape(data,(None,dtf.COLS_TOTAL)), tf.ensure_shape(target, (None,dtf.COLS_TARGET))))
    #dataset = dataset.map(lambda data,target: (tf.set_shape(data,(None,dtf.COLS_TOTAL)), tf.set_shape(target, (None,dtf.COLS_TARGET))))
    
    return dataset

def train_valid_test(tfrecords_dir=None, seed=623, train_frac=0.7, valid_frac=0.2, singular_plays_keep_prob=0.1):
    if tfrecords_dir is None:
        tfrecords_dir = '/staging/fast/taylora/euchre/tfrecords' if os.path.exists('/staging/fast/') else os.path.join(os.getcwd(), 'tfrecords')
    tfrecord_paths = [os.path.join(tfrecords_dir, f) for f in os.listdir(tfrecords_dir) if '.tfrecord' in f]
    np.random.seed(int(seed))
    tf.set_random_seed(int(seed))
    np.random.shuffle(tfrecord_paths)

    #train_frac = 0.7; valid_frac=0.2; test_frac=1-train_frac-valid_frac # don't need to have this last bit, but eh
    TRAIN = get_dataset(tfrecord_paths[:int(train_frac*len(tfrecord_paths))], singular_plays_keep_prob=singular_plays_keep_prob)
    VALID = get_dataset(tfrecord_paths[int(train_frac*len(tfrecord_paths)):int((train_frac+valid_frac)*len(tfrecord_paths))], singular_plays_keep_prob=singular_plays_keep_prob)
    TEST  = get_dataset(tfrecord_paths[int((train_frac+valid_frac)*len(tfrecord_paths)):], singular_plays_keep_prob=singular_plays_keep_prob)
    
    return TRAIN, VALID, TEST

def remove_singular_plays(data, target, keep_prob=0.1):
    # find ixs of single-option plays
    # assume inputs are numpy arrays
    singular_ixs = set()
    if len(data.shape) == 1: data = np.array([data])
    if len(target.shape) == 1: target = np.array([target])
        
    count_finaltrick, count_followsuit = 0,0
    for i in range(len(data)):
        row = data[i]
        COLS_COUNTS = [0, dtf.COLS_GROUP1, dtf.COLS_GROUP2, dtf.COLS_GROUP3, dtf.COLS_GROUP4]
        group1, group2, group3, group4 = [row[sum(COLS_COUNTS[:(i+1)]) : sum(COLS_COUNTS[:(i+2)])  ] for i in range(len(COLS_COUNTS)-1)]
        
        # self maps to 3 -- (0, 1, 2, 3)
        count_cards_remaining = sum(group3[3::int(dtf.COLS_GROUP3/24)])
        # alternate method -- use group4
        #count_cards_remaining = int(sum(  [sum(group4[11*i:11*(i+1)][:-1]) for i in range(5)]  )/2)
        if count_cards_remaining == 1:
            count_finaltrick += 1
            singular_ixs.add(i)
            continue
        
        led_suit = 0*group2[4+4+6 + 0] + 1*group2[4+4+6 + 1] + 2*group2[4+4+6 + 2] + 3*group2[4+4+6 + 3]
        led_trump = group2[4+4+7 + 4]
        
        if led_trump:
            trumps_in_hand = sum(group4[10::11])
            if trumps_in_hand == 1:
                count_followsuit += 1
                singular_ixs.add(i)
                continue
        else:
            followsuits_in_hand = sum([c[6+led_suit] and not c[-1] for c in [group4[11*i:11*(i+1)] for i in range(5)]])
            if followsuits_in_hand == 1:
                count_followsuit += 1
                singular_ixs.add(i)
                continue
                
    # it's like 50% of all plays -- 50% of those are following suit, and 50% are final trick (why 25% of the total instead of 20%?)            
    #print('Singular fraction:             %.2f (%i / %i)' %(len(singular_ixs)/len(data), len(singular_ixs), len(data)))
    #print('Singular follow suit fraction: %.2f (%i / %i)' %(count_followsuit/len(singular_ixs), count_followsuit, len(singular_ixs)))
    #print('Singular final trick fraction: %.2f (%i / %i)' %(count_finaltrick/len(singular_ixs), count_finaltrick, len(singular_ixs)))
    keep_ixs = [i for i in singular_ixs if np.random.random() < keep_prob]
    keep_ixs = np.array(keep_ixs + [i for i in range(len(data)) if i not in singular_ixs])
    
    return data[keep_ixs], target[keep_ixs]