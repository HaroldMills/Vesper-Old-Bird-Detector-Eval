"""
Runs the Vesper reimplementations of the Old Bird Tseep and Thrush detectors
on the BirdVox-full-night recordings.

This script runs the Vesper reimplementations of the Old Bird Tseep and
Thrush detectors on all of the BirdVox-full-night recordings with multiple
detection thresholds. It writes metadata for the resulting detections to an
output CSV file for further processing, for example for plotting precision
vs. recall curves.

Both detectors are run both with and without the post-processing steps
performed by the original Old Bird detectors, including the merging of
overlapping clips and the suppression of frequent clips.

The inputs required by this script are:

1. The BirdVox-full-night recordings, as WAV files. The BirdVox-full-night
dataset includes the recordings as FLAC files: you can use Sox
(http://sox.sourceforge.net/) or some other software to convert the FLAC
files to WAV files. The directory containing the WAV files is specified
by eval.utils.RECORDINGS_DIR_PATH.

The outputs produced by this script are:

1. The files "Old Bird Clips (no post).csv" and
"Old Bird Clips (with post).csv", containing the results of detector
runs with and without the post-processing steps of the original Old Bird
detectors, respectively. Each line of these files contains data describing
one clip produced by a detector. The directory to which these files are
written is specified by eval.utils.WORKING_DIR_PATH.
"""


import csv
import math
import time

import numpy as np

from eval.old_bird_detector_redux_1_1_mt import ThrushDetector, TseepDetector
from eval.wave_file_reader import WaveFileReader
import eval.utils as utils


# Set this `True` to run detectors on first recording only.
QUICK_RUN = False

DETECTOR_CLASSES = {
    'Thrush': ThrushDetector,
    'Tseep': TseepDetector
}

# Wave file read chunk size in samples.
CHUNK_SIZE = 100000


def main():
    run_detectors_on_all_recordings(False)
    run_detectors_on_all_recordings(True)
    
    
def run_detectors_on_all_recordings(post_enabled):
    
    listeners = create_listeners()
    
    for unit_num in utils.UNIT_NUMS:
        
        run_detectors_on_one_recording(unit_num, post_enabled, listeners)
            
        if QUICK_RUN:
            break
            
    write_detections_file(post_enabled, listeners)
    
    
def create_listeners():
    names = sorted(DETECTOR_CLASSES.keys())
    return [Listener(name) for name in names]
    
    
def run_detectors_on_one_recording(unit_num, post_enabled, listeners):
        
    file_path = utils.get_recording_file_path(unit_num)
    post_state = 'enabled' if post_enabled else 'disabled'
        
    print((
        'Running detectors with post-processing {} on file '
        '"{}"...').format(post_state, file_path))
    
    for listener in listeners:
        listener.unit_num = unit_num
    
    start_time = time.time()
    
    reader = WaveFileReader(str(file_path))
    num_chunks = int(math.ceil(reader.length / CHUNK_SIZE))
    sample_rate = reader.sample_rate
    
    detectors = \
        [create_detector(sample_rate, post_enabled, l) for l in listeners]
        
    for i, samples in enumerate(generate_sample_buffers(reader)):
        if i != 0 and i % 1000 == 0:
            print('    Chunk {} of {}...'.format(i, num_chunks))
        for detector in detectors:
            detector.detect(samples[0])
                       
    for detector in detectors:
        detector.complete_detection()

    reader.close()
    
    processing_time = time.time() - start_time
    file_duration = reader.length / sample_rate
    show_processing_time(processing_time, file_duration)
        

def create_detector(sample_rate, post_enabled, listener):
    cls = DETECTOR_CLASSES[listener.name]
    thresholds = get_detection_thresholds(utils.DETECTION_THRESHOLDS_POWER)
    return cls(thresholds, post_enabled, sample_rate, listener)


def get_detection_thresholds(p):

    min_t = utils.MIN_DETECTION_THRESHOLD
    max_t = utils.MAX_DETECTION_THRESHOLD
    n = utils.NUM_DETECTION_THRESHOLDS
    y = (np.arange(n) / (n - 1)) ** p
    t = min_t + (max_t - min_t) * y
    t = list(t)
    
    # Always include Old Bird Tseep and Thrush thresholds.
    t.append(1.3)   # Thrush
    t.append(2)     # Tseep
    
    t.sort()
    
    return t


def generate_sample_buffers(file_reader):
    
    start_index = 0
    
    while start_index < file_reader.length:
        length = min(CHUNK_SIZE, file_reader.length - start_index)
        yield file_reader.read(start_index, length)
        start_index += CHUNK_SIZE


def show_processing_time(processing_time, file_duration):
    factor = file_duration / processing_time
    print(
        ('Ran detectors on {}-second file in {} seconds, {} times faster '
         'than real time.').format(
             round_(file_duration), round_(processing_time), round_(factor)))
        
        
def round_(t):
    return round(10 * t) / 10


def write_detections_file(post_enabled, listeners):
    
    file_path = utils.get_old_bird_clips_file_path(post_enabled)
    
    with open(file_path, 'w') as file_:
        
        writer = csv.writer(file_)
        
        writer.writerow(
            ['Detector', 'Unit', 'Threshold', 'Start Index', 'Length'])
        
        for listener in listeners:
            
            print('{} detector produced {} clips.'.format(
                listener.name, len(listener.clips)))
            
            listener.clips.sort()
            
            writer.writerows(listener.clips)


class Listener:
    
    
    def __init__(self, name):
        self.name = name
        self.unit_num = None
        self.clips = []
        
        
    def process_clip(self, start_index, length, threshold):
        self.clips.append(
            [self.name, self.unit_num, threshold, start_index, length])
        
        
if __name__ == '__main__':
    main()
