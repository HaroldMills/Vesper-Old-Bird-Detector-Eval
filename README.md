# Vesper-Old-Bird-Detector-Eval
Python scripts that evaluate the [Vesper](https://github.com/HaroldMills/Vesper) reimplementations of the [Old Bird Tseep and Thrush](http://www.oldbird.org/analysis.htm) nocturnal flight call detectors on the [BirdVox-full-night](https://wp.nyu.edu/birdvox/birdvox-full-night/) recordings.

The original Old Bird Tseep and Thrush detectors were developed by [Old Bird, Inc.](http://www.oldbird.org/) in the late 1990s for acoustical nocturnal migration monitoring. The original detectors ran only on the Windows operating system, they assumed an input sample rate of 22050 hertz, and they could only run on one input file on a given computer at once. The detectors were reimplemented as part of the Vesper project in 2017 to remove these limitations, and to provide baseline detectors to which new detectors could more easily be compared.

This repository contains Python scripts that measure the recall and precision of the reimplemented Old Bird detectors on the recordings of the [BirdVox-full-night dataset](http://doi.org/10.5281/zenodo.1205569) [1]. That dataset contains six full-night recordings made in the Ithaca, New York area on September 23, 2015, along with expert manual annotations of all of the nocturnal flight calls that occur in the recordings. The manual annotations provide the ground truth that code in this repository uses to measure detector recall and precision.

There are two scripts in the repository, `run_old_bird_detectors.py` and `evaluate_old_bird_detectors.py`. `run_old_bird_detectors.py` runs the reimplemented Old Bird detectors on all six of the the BirdVox-full-night recordings for multiple detection thresholds. It runs each detector twice on each recording for each threshold, once with certain post-processing steps (including steps that merge overlapping detections and suppress frequent detections) that were included in the original Old Bird detectors, and once without those steps. It writes the resulting detections to the CSV files `Old Bird Clips (with post).csv` and `Old Bird Clips (no post).csv`.

The `evaluate_old_bird_detectors.py` script uses the ground-truth call center times and frequencies provided by the BirdVox-full-night dataset to automatically classify each detection produced by the reimplemented Old Bird detectors as either a true (i.e. a call) detection or a false detection. It then plots precision vs. recall curves using those classifications. It creates one plot for the detectors run with the post-processing of the original Old Bird detectors, and one for the detectors run without that post-processing. It writes the plots to the PDF files `Old Bird Detector Precision vs. Recall (with post).pdf` and `Old Bird Detector Precision vs. Recall (no post).pdf`.

The plots show precision vs. recall measured both separately for each detector (the orange and blue lines, with the orange and blue dots marking the precision and recall of the detectors run with the detection thresholds of the original Old Bird detectors) and for the two detectors combined (the green line). The separated Tseep and Thrush curves are computed considering only calls whose annotated center frequencies are above and below 5000 hertz, respectively. The combined curve is computed considering all calls, with the Tseep and Thrush detectors constrained to share a detection threshold and responsible for detecting calls with center frequencies above and below 5000 hertz, respectively. In practice, one would use different thresholds for the two detectors for improved performance: the combined curve is included for comparison to the "Old Bird" curve of [Lostanlen et al. 2018](http://www.justinsalamon.com/uploads/4/3/9/4/4394963/lostanlen_birdvox-full-night_icassp_2018.pdf) [2].

Comparison of the two plots shows that, at least in some cases, the post-processing of the original Old Bird detectors can reduce detector recall and precision. In particular, the plots show a reduction in both recall and precision for the Thrush detector. The clip suppression post-processing step was intended to increase detector precision in situations in which a noise source at a recording site causes frequent false detections, but it appears that in some situations, such as when there are frequent thrush calls, such processing can also decrease precision.

To run the scripts of this repository to reproduce the precision vs. recall plots:

1. Download the [BirdVox-full-night](https://wp.nyu.edu/birdvox/birdvox-full-night) dataset.

2. Convert the full-night FLAC recordings of the dataset to WAV format. There are various ways to do this: one is to use [SoX](http://sox.sourceforge.net/). For example, to use SoX to convert a FLAC file `myfile.flac` to WAV format:

        sox myfile.flac myfile.wav
    
3. Create a new [Conda](https://conda.io) environment that includes the dependencies of the scripts of this repository:

        conda create -n old-bird-detector-eval scipy matplotlib pandas
    
4. Activate the new environment. On Windows:

        activate old-bird-detector-eval
        
    or on macOS or Linux:
    
        source activate old-bird-detector-eval
    
5. Clone this repository to your computer:

        git clone https://github.com/HaroldMills/Vesper-Old-Bird-Detector-Eval.git

6. Edit the file `eval/utils.py` of your cloned repository, setting the values of the `RECORDINGS_DIR_PATH`, `ANNOTATIONS_DIR_PATH`, and `WORKING_DIR_PATH` constants for your installation.

7. Run the scripts of the repository. From your repository directory:

        python run_old_bird_detectors.py
        python evaluate_old_bird_detectors.py
    
    The first script runs in about two hours on a 2012 MacBook Pro. The second script runs in about two minutes. For more details about the operation of the scripts, see the module docstrings of the scripts.
    
Thanks to the BirdVox team for creating the valuable BirdVox-full-night dataset.
    
This repository is part of the [Vesper](https://github.com/HaroldMills/Vesper) project.

## References

1. Lostanlen, Vincent, Salamon, Justin, Farnsworth, Andrew, Kelling, Steve, & Bello, Juan Pablo. (2017).
   BirdVox-full-night: a dataset for avian flight call detection in continuous recordings (Version 3.0) [Data set].
   Zenodo. http://doi.org/10.5281/zenodo.1205569
    
2. Lostanlen, Vincent, Salamon, Justin, Farnsworth, Andrew, Kelling, Steve, & Bello, Juan Pablo. (2018).
   BirdVox-full-night: A dataset and benchmark for avian flight call detection.
   *Proc. IEEE ICASSP*, 2018.
   http://www.justinsalamon.com/uploads/4/3/9/4/4394963/lostanlen_birdvox-full-night_icassp_2018.pdf
    
![Image of Zenodo DOI badge](https://zenodo.org/badge/DOI/10.5281/zenodo.1292122.svg)

    
