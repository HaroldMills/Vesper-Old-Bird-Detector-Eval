"""
Plots precision vs. recall curves for the Vesper reimplementations of
the Old Bird Tseep and Thrush detectors run on the BirdVox-full-night
recordings.

This script plots curves for the detectors run both with and without the
post-processing steps performed by the Old Bird detectors, including the
merging of overlapping clips and the suppression of frequent clips.

The inputs required by this script are:

1. The files "Old Bird Clips (no post).csv" and
"Old Bird Clips (with post).csv" produced by the run_old_bird_detectors
script. The directory containing these files is specified by
eval.utils.WORKING_DIR_PATH.

2. The BirdVox-full-night CSV annotation files, as distributed with the
BirdVox-full-night dataset. The directory containing these files is
specified by eval.utils.ANNOTATIONS_DIR_PATH.

The outputs produced by this script are:

1. The files "Old Bird Detector Precision vs. Recall (no post).pdf"
and "Old Bird Detector Precision vs. Recall (with post).pdf", containing
plots of the precision vs. recall curves. The directory to which these
files are written is specified by eval.utils.WORKING_DIR_PATH.
"""


from collections import defaultdict
import csv

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import eval.utils as utils


def main():
    evaluate_detectors(False)
    evaluate_detectors(True)
    
    
def evaluate_detectors(post_enabled):
    
    old_bird_clips = get_old_bird_clips(post_enabled)
    show_old_bird_clip_counts(old_bird_clips)
        
    ground_truth_call_centers = get_ground_truth_call_centers()
    show_ground_truth_call_counts(ground_truth_call_centers)
    
    rows = count_old_bird_calls(old_bird_clips, ground_truth_call_centers)
    
    raw_df = create_raw_df(rows)
    separated_df = create_separated_detectors_df(raw_df)
    merged_df = create_merged_detectors_df(separated_df)
    
    add_precision_recall_f1(raw_df)
    add_precision_recall_f1(separated_df)
    add_precision_recall_f1(merged_df)
    
    print(raw_df.to_csv())
    print(separated_df.to_csv())
    print(merged_df.to_csv())
    
    plot_precision_vs_recall(post_enabled, separated_df, merged_df)
    
    
def get_old_bird_clips(post_enabled):
    
    file_path = utils.get_old_bird_clips_file_path(post_enabled)
    clips = defaultdict(list)
        
    with open(file_path) as file_:
        
        reader = csv.reader(file_)
        
        # Skip header.
        next(reader)
        
        for row in reader:
            key = (row[0], int(row[1]), float(row[2]))
            value = (int(row[3]), int(row[4]))
            clips[key].append(value)
            
    return clips


def show_old_bird_clip_counts(clips):
    print('Old Bird clip counts:')
    keys = sorted(clips.keys())
    for key in keys:
        print('   ', key, len(clips[key]))


def get_ground_truth_call_centers():
     
    centers = defaultdict(list)
     
    for unit_num in utils.UNIT_NUMS:
         
        file_path = utils.get_annotations_file_path(unit_num)
         
        with open(file_path) as file_:
             
            reader = csv.reader(file_)
             
            # Skip header.
            next(reader)
             
            for row in reader:
                 
                time = float(row[0])
                index = utils.seconds_to_samples(time)
                 
                freq = int(row[1])
                call_type = get_call_type(freq)
                     
                key = (call_type, unit_num)
                centers[key].append(index)
    
    # Make sure center index lists are sorted.
    for indices in centers.values():
        indices.sort()
        
    return centers
                    
                    
def get_call_type(freq):
    return 'Tseep' if freq >= utils.FREQ_THRESHOLD else 'Thrush'


def show_ground_truth_call_counts(call_centers):
    print('Ground truth call counts:')
    keys = sorted(call_centers.keys())
    for key in keys:
        print('   ', key, len(call_centers[key]))
    
    
def count_old_bird_calls(old_bird_clips, ground_truth_call_center_indices):
    
    rows = []
    
    for (detector_name, unit_num, threshold), clips in old_bird_clips.items():
        
        call_center_indices = \
            ground_truth_call_center_indices[(detector_name, unit_num)]
        window = utils.OLD_BIRD_CLIP_CALL_CENTER_WINDOWS[detector_name]
        
        matches = match_clips_with_calls(clips, call_center_indices, window)
        old_bird_call_count = len(matches)
        
        old_bird_clip_count = len(clips)
        ground_truth_call_count = len(call_center_indices)
        
        rows.append([
            detector_name, unit_num, threshold, ground_truth_call_count,
            old_bird_call_count, old_bird_clip_count])

    return rows


def match_clips_with_calls(clips, call_center_indices, window):
    
    clip_count = len(clips)
    
    matches = []
    i = 0
    
    for j, call_center_index in enumerate(call_center_indices):
        
        while i != clip_count and \
                get_end_index(clips[i]) <= call_center_index:
            # Old Bird clip i ends before call center
            
            i += 1
            
        if i == clip_count:
            # no more Old Bird clips
            
            break
            
        # At this point Old Bird clip i is the first Old Bird clip
        # that has not already been paired with a call center and
        # that ends after call center j.
        
        if is_call_detection(clips[i], call_center_index, window):
                
            matches.append((i, j))
            # Increment i to ensure that we match each Old Bird clip
            # with at most one ground truth call. This is conservative,
            # since some Old Bird clips contain more than one ground
            # truth call.
            i += 1
            
    return matches
            

def get_end_index(clip):
    start_index, length = clip
    return start_index + length


def is_call_detection(clip, call_center_index, window):
    
    """
    Tests if the specified Old Bird clip should count as a detection of
    a call with the specified center index, i.e. if the center index is
    within the specified detection window within the clip.
    """
    
    clip_start_index, clip_length = clip
    clip_end_index = clip_start_index + clip_length
    window_start_offset, window_length = window
    window_start_index = clip_start_index + window_start_offset
    window_end_index = min(window_start_index + window_length, clip_end_index)
    return window_start_index <= call_center_index and \
        call_center_index < window_end_index


def create_raw_df(rows):
    
    columns = [
        'Detector', 'Unit', 'Threshold', 'Ground Truth Calls',
        'Old Bird Calls', 'Old Bird Clips']
    
    return pd.DataFrame(rows, columns=columns)


def create_separated_detectors_df(df):
    df = df.drop(columns=['Unit'])
    grouped = df.groupby(['Detector', 'Threshold'], as_index=False)
    return grouped.aggregate(np.sum)


def create_merged_detectors_df(df):
    df = df.drop(columns=['Detector'])
    grouped = df.groupby(['Threshold'], as_index=False)
    return grouped.aggregate(np.sum)


def sum_counts(df, detector):
    
    if detector != 'All':
        df = df.loc[df['Detector'] == detector]
    
    return [
        detector,
        df['Ground Truth Calls'].sum(),
        df['Old Bird Calls'].sum(),
        df['Old Bird Clips'].sum()]
    
        
def add_precision_recall_f1(df):
    p = df['Old Bird Calls'] / df['Old Bird Clips']
    r = df['Old Bird Calls'] / df['Ground Truth Calls']
    df['Precision'] = to_percent(p)
    df['Recall'] = to_percent(r)
    df['F1'] = to_percent(2 * p * r / (p + r))


def to_percent(x):
    return round(1000 * x) / 10


def plot_precision_vs_recall(post_enabled, separated_df, merged_df):
    
    file_path = utils.get_precision_vs_recall_plot_file_path(post_enabled)
    
    with PdfPages(file_path) as pdf:
        
        _, axes = plt.subplots(figsize=(6, 6))
        
        detector_data = {
            ('Tseep', 2, 'C0'),
            ('Thrush', 1.3, 'C1'),
        }
        
        # Plot separate detector curves.
        for detector_name, threshold, color in detector_data:
            
            # Plot curve.
            df = separated_df.loc[separated_df['Detector'] == detector_name]
            precisions = df['Precision'].values
            recalls = df['Recall'].values
            axes.plot(recalls, precisions, color=color, label=detector_name)
            
            # Put marker at Old Bird detector point.
            indices = dict(
                (t, i) for i, t in enumerate(df['Threshold'].values))
            i = indices[threshold]
            axes.plot([recalls[i]], [precisions[i]], marker='o', color=color)
            
        # Plot merged curve.
        precisions = merged_df['Precision'].values
        recalls = merged_df['Recall'].values
        axes.plot(recalls, precisions, color='C2', label='Tseep and Thrush')
        
        plt.xlabel('Recall (%)')
        plt.ylabel('Precision (%)')
        limits = (0, 100)
        plt.xlim(limits)
        plt.ylim(limits)
        major_locator = MultipleLocator(25)
        minor_locator = MultipleLocator(5)
        axes.xaxis.set_major_locator(major_locator)
        axes.xaxis.set_minor_locator(minor_locator)
        axes.yaxis.set_major_locator(major_locator)
        axes.yaxis.set_minor_locator(minor_locator)
        plt.grid(which='both')
        plt.grid(which='minor', alpha=.4)
        axes.legend()
        post_string = utils.get_post_string(post_enabled)
        plt.title(
            'Old Bird Detector Precision vs. Recall ({})'.format(post_string))
        
        pdf.savefig()
        
        # plt.show()
    
    
if __name__ == '__main__':
    main()
