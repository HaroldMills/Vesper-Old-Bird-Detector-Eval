"""
Utility constants and functions for Old Bird detector evaluation.

Edit the RECORDINGS_DIR_PATH, ANNOTATIONS_DIR_PATH, and WORKING_DIR_PATH
constants below to set the input and output directories for the
run_old_bird_detectors and evaluate_old_bird_detectors scripts.

Edit NUM_DETECTION_THRESHOLDS to adjust the number of detection
thresholds for which the detectors are run. Reducing the number of
thresholds speeds up detector runs considerably during testing.
"""


from pathlib import Path


RECORDINGS_DIR_PATH = Path(
    '/Users/harold/Desktop/NFC/Data/BirdVox/BirdVox-full-night/Other/'
    'Recording Wave Files')

ANNOTATIONS_DIR_PATH = Path(
    '/Users/harold/Desktop/NFC/Data/BirdVox/BirdVox-full-night/Dataset')

WORKING_DIR_PATH = Path('/Users/harold/Desktop')

RECORDING_FILE_NAME_FORMAT = 'BirdVox-full-night_wav-audio_unit{:02}.wav'

ANNOTATIONS_FILE_NAME_FORMAT = \
    'BirdVox-full-night_csv-annotations_unit{:02}.csv'

OLD_BIRD_CLIPS_FILE_NAME_FORMAT = 'Old Bird Clips ({}).csv'

PRECISION_VS_RECALL_PLOT_FILE_NAME_FORMAT = \
    'Old Bird Detector Precision vs. Recall ({}).pdf'

UNIT_NUMS = (1, 2, 3, 5, 7, 10)

# Constants determining the thresholds for which detectors are run.
# The Old Bird Tseep and Thrush thresholds (2 and 1.3, respectively)
# are added to those generated from these constants.
MIN_DETECTION_THRESHOLD = 1.05
MAX_DETECTION_THRESHOLD = 20
DETECTION_THRESHOLDS_POWER = 3
NUM_DETECTION_THRESHOLDS = 100

# Center frequency threshold separating tseep and thrush calls, in hertz.
FREQ_THRESHOLD = 5000

# Recording sample rate, in hertz.
SAMPLE_RATE = 24000


def seconds_to_samples(x):
    return int(round(x * SAMPLE_RATE))


# Windows of Old Bird clips that must contain a BirdVox-full-night
# call center in order for the clip to be counted as a call. The
# windows begin a fixed offset (90 ms for tseep clips and 150 ms
# for thrush clips, reflecting the different amounts of initial
# padding that the detectors add to their clips) from the beginnings
# of clips and have a duration of 200 ms.
OLD_BIRD_CLIP_CALL_CENTER_WINDOWS = {
    'Tseep': (seconds_to_samples(.09), seconds_to_samples(.2)),
    'Thrush': (seconds_to_samples(.15), seconds_to_samples(.2))
}


def get_recording_file_path(unit_num):
    file_name = RECORDING_FILE_NAME_FORMAT.format(unit_num)
    return RECORDINGS_DIR_PATH / file_name


def get_annotations_file_path(unit_num):
    file_name = ANNOTATIONS_FILE_NAME_FORMAT.format(unit_num)
    return ANNOTATIONS_DIR_PATH / file_name


def get_old_bird_clips_file_path(post_enabled):
    post_string = get_post_string(post_enabled)
    file_name = OLD_BIRD_CLIPS_FILE_NAME_FORMAT.format(post_string)
    return WORKING_DIR_PATH / file_name


def get_post_string(post_enabled):
    return 'with post' if post_enabled else 'no post'


def get_precision_vs_recall_plot_file_path(post_enabled):
    post_string = get_post_string(post_enabled)
    file_name = PRECISION_VS_RECALL_PLOT_FILE_NAME_FORMAT.format(post_string)
    return WORKING_DIR_PATH / file_name
