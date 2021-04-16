import numpy as np
import os
import sys
import tensorflow as tf
tf.compat.v1.enable_eager_execution()
print(tf.__version__)
import time
import pandas as pd
import data_formatting as dtf

###################################
def get_next_file(datafolder, skipfiles_path):
    with open(skipfiles_path, 'r') as f:
        lines = f.read()
    skipfiles = lines.split('\n')
    for f in os.listdir(datafolder):
        f = os.path.join(datafolder, f)
        if '.csv' not in f:
            continue
        if '_hands_' not in f:
            continue
        if f.split('/')[-1] in [skipfile.split('/')[-1] for skipfile in skipfiles]:
            continue
        return f

def reserve_file(skipfiles_path, file):
    with open(skipfiles_path, 'a') as outfile:
        outfile.write(file+'\n')
        
def unreserve_file(skipfiles_path, file):
    with open(skipfiles_path, 'r') as f:
        lines = f.read()
    output = '\n'.join([l for l in lines.split('\n') if l!=file])
    with open(skipfiles_path, 'w') as f:
        f.write(output)
###################################
#
#
#
###################################
def format_onefile(infile):
    df = pd.read_csv(infile)
    data, target = dtf.format_data(df)
    return data, target
###################################
#
#
#
###################################
def data_to_tfrecord(data, target, tfrecords_folder, ogfile_name):
    outfile = os.path.join(tfrecords_folder, ogfile_name.split('/')[-1].split('.csv')[0] + '.tfrecord')
    with tf.io.TFRecordWriter(outfile) as tfrec:
        dataset = tf.data.Dataset.from_tensor_slices((np.expand_dims(data, axis=0), np.expand_dims(target, axis=0)))
        for d, t in dataset.take(1):
            example = serialize_example(tf.io.serialize_tensor(d), tf.io.serialize_tensor(t))
        tfrec.write(example)

def serialize_example(data, target):
    feature = {
        'data':bytes_feature(data),
        'target':bytes_feature(target)
    }
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()

def bytes_feature(value):
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy()
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))
###################################
#
#
#
###################################
def run_file(datafolder, tfrecords_folder, count=None, dt_stop=None, skipfile_name=None):
    if not os.path.exists(tfrecords_folder): os.mkdir(tfrecords_folder)
    skipfiles_path = os.path.join(tfrecords_folder, 'skipfiles.txt' if skipfile_name is None else skipfile_name)
    with open(skipfiles_path, 'a') as f:
        f.write('')
    
    try:
        if count is not None:
            for i in range(int(count)):
                next_file = get_next_file(datafolder, skipfiles_path)
                print('Starting file %s...' %next_file)
                reserve_file(skipfiles_path, next_file)
                data, target = format_onefile(next_file)
                data_to_tfrecord(data, target, tfrecords_folder, next_file)
        elif dt_stop is not None:
            tstart = time.time()
            while time.time() - tstart < dt_stop:
                next_file = get_next_file(datafolder, skipfiles_path)
                print('Starting file %s...' %next_file)
                reserve_file(skipfiles_path, next_file)
                data, target = format_onefile(next_file)
                data_to_tfrecord(data, target, tfrecords_folder, next_file)
        else:
            # just do one
            next_file = get_next_file(datafolder, skipfiles_path)
            print('Starting file %s...' %next_file)
            reserve_file(skipfiles_path, next_file)
            data, target = format_onefile(next_file)
            data_to_tfrecord(data, target, tfrecords_folder, next_file)
    except KeyboardInterrupt:
        print('Unreserving file %s' %next_file)
        unreserve_file(skipfiles_path, next_file)
        raise KeyboardInterrupt
    except:
        print('Unreserving file %s' %next_file)
        unreserve_file(skipfiles_path, next_file)
        print("Unexpected error:", sys.exc_info()[0])
        raise
    
    print('Done!')
###################################
#
#
#
###################################
def read_one(serialized_example):
    feature_description = {
        'data':tf.io.FixedLenFeature((), tf.string),
        'target':tf.io.FixedLenFeature((), tf.string)
    }
    example = tf.io.parse_single_example(serialized_example, feature_description)
    data = tf.io.parse_tensor(example['data'], tf.int8)
    target = tf.io.parse_tensor(example['target'], tf.int8)
    return data, target

def read_dataset(path):
    path = 'tfrecords/10000_hands_403.tfrecord'
    dataset = tf.data.TFRecordDataset(path)
    dataset = dataset.map(read_one)
    return dataset
###################################
#
#
#
###################################
if __name__ == "__main__":
    if os.path.exists('/staging/fast'):
        ROOT = '/staging/fast/taylora/euchre/'
        dt_stop = 23*3600
    else:
        ROOT = ''
        dt_stop = None
    
    datafolder = os.path.join(ROOT, 'RLdataset')
    tfrecords_folder = os.path.join(ROOT, 'tfrecords')
    run_file(datafolder, tfrecords_folder, dt_stop=dt_stop)
    