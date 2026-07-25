# Geotaxis Files

A hardware–software pipeline for fully automated, high-throughput negative geotaxis (climbing) assays in Drosophila melanogaster. The system pairs a 3D-printed, motorized 12-vial recording rig with an end-to-end Python/PyTorch analysis pipeline that converts raw video directly into time-resolved climbing metrics and statistical comparisons across genotypes, sexes, and ages, with no manual scoring or frame-by-frame human intervention required.


## System Overview & Purpose

Traditional negative geotaxis scoring requires a researcher to manually pause video at a fixed endpoint, draw a reference line, and tally the fraction of flies above it which is a process that is slow, low-resolution (a single data point per vial per trial), and subject to observer bias.

This pipeline replaces that workflow with continuous, population-level video tracking: raw H.264 recordings from the accompanying Raspberry Pi–based hardware rig are automatically converted, split into individual climbing trials, and analyzed frame-by-frame to extract climbing position, velocity, and zone occupancy for every vial, fully automatically, then statistically compared across user-specified genotype and age groups.


## Hardware 

The recording apparatus (STL files in main_stl_files_and_folders/) consists of:
- A custom 3D-printed 12-position vial holder and third-class-lever tapping mechanism, driven by a DC motor via an L298N motor driver module
- A Raspberry Pi 4B, controlling both the tapping motor (via GPIO) and video capture
- A Raspberry Pi HQ Camera (12.3 MP Sony IMX477 sensor) with a 6 mm CS-mount lens, recording at 60 fps, 1280×720
- A fixed lamp light source, positioned to eliminate glare and standardize illumination for background subtraction

A Python control script (run on the Pi) automatically executes four tap–climb cycles per recording: each cycle taps the vial rack (grounding the flies), then records a 15-second quiescent climbing window, for a total of four independent climbing trials per video file.

Full assembly instructions, GPIO pin assignments, and a complete bill of materials are provided in the manuscript's Supplementary Information.


## Core Features & Capabilities

**Vial detection**

- Custom-trained Faster R-CNN (ResNet-50 + Feature Pyramid Network) object detector, trained from scratch (no pretrained weights) on 1,140 annotated frames / 13,680 vial instances
- Inference filtered at confidence ≥ 0.85, with left-to-right spatial sorting of detected vials
- Achieves mean IoU > 0.95 against manual annotations on held-out validation frames

**Fly detection and zone classification**

- Per-pixel-max background subtraction (red-channel isolation) computed independently for each trimmed video
- Connected-component analysis to extract fly centroids per frame, filtered by area
- Each centroid assigned to a vial and classified into Low / Middle / High Performer (LP / MP / HP) vertical zones based on y-position, enabling continuous zone-occupancy tracking (not just an endpoint threshold)
- Population-level (not identity-preserving) tracking: all fly positions within a vial are averaged at each frame, avoiding identity-switching errors that arise from occlusion during climbing

**Video processing**

- Automated H.264 → MP4 conversion (ffmpeg, lossless quality settings)
- Automatic trial splitting into four 15-second clips via OpenCV MOG2 motion detection and SciPy peak/inactivity detection; no manual round definition required

**Statistical analysis**

- Linear Mixed-Effects (LME) models (Statsmodels, REML) with fixed effects for genotype, time, and their interaction, and random intercepts/slopes per vial to properly account for autocorrelated, repeated-measures data
- Harmonic Mean p-value (HMP) combination across correlated LME terms per genotype comparison
- Time-resolved Mann–Whitney U tests at each discrete timepoint, visualized as –log₁₀(p) significance heatmaps
- Peak-position summary bar plots with embedded significance annotations and replicate counts (N)

**Automation and batch processing**
- Iterates automatically over an arbitrary number of experiment/video subfolders
- Skips subfolders that have already been fully processed, enabling safe resumption of interrupted runs
- Aggregates results into sex-specific ("Output Males" / "Output Females") summary CSVs and plots across all processed videos


## Execution Pipeline Walkthrough

The pipeline runs in three sequential stages, orchestrated by MAIN_geotaxis.py (or interactively via gt_full_process.ipynb), and is also available as a standalone GUI executable for Windows, macOS, and Ubuntu Linux (no Python installation required).

### Stage 1: Recording

Assemble the hardware rig, load vials into the 12-position holder, and record via the on-device Python script. Each recording folder must contain the raw .h264 video and a geotaxis_metadata.csv file (columns: Vial_Num, Genotype, Sex, n), named identically to the video file. Recording folders are organized under a single top-level experiment directory (see Repository Structure below).

### Stage 2: Processing

For each unprocessed video subfolder, the pipeline automatically:
1. Converts the .h264 file to .mp4
2. Splits the video into four 15-second trimmed climbing trials via motion detection
3. Detects and spatially sorts vials with the Faster R-CNN model
4. Tracks fly centroids per frame and classifies them into LP/MP/HP zones
5. Subsamples to 2 Hz and converts pixel/frame units to centimeters/seconds
6. Writes per-trial CSVs and diagnostic plots

### Stage 3: Aggregation and Statistics

- Aggregates all per-trial outputs into wide-form, sex-specific summary tables (position, velocity, LP%, MP%, HP%) across replicates
- Computes climbing velocity as the numerical gradient of mean position over time
- Fits LME models and runs time-resolved Mann–Whitney U tests for a user-specified control genotype vs. one or more comparison genotypes, over a user-defined time window
- Outputs annotated trajectory plots, peak-position bar plots, and significance heatmaps

## Quantified Behavioral & Kinematic Metrics

| Metric          | Unit    | Description                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Position          | cm      | Mean climbing height across all tracked flies in a vial at each timepoint, calibrated from pixel coordinates via chamber height (17 cm / 720 px).                                                                                                                                                                                                                                                                 |
| Velocity           | cm/s    | 	Instantaneous climbing speed, computed as the numerical gradient of mean position over time.                                                                                                                                                                                                                                                           |
| Low Performer (LP)    | %  | Percentage of tracked flies in the lowest vertical zone of the vial at each timepoint.                                                                                                                                                                                                                                       |
| Middle Performer (MP)        | %      | Percentage of tracked flies in the middle vertical zone at each timepoint.                                                                                                                                                                                                                                                                                                                                                  |
| High Performer (HP)         | % | Percentage of tracked flies in the highest vertical zone at each timepoint.                                                                                                                                                                                                                                                                                                                                                     |
---

## Repository Structure
 
```
geotaxis_files/
├── MAIN_geotaxis.py            # Entry point for the full pipeline
├── gt_full_process.ipynb       # Interactive Jupyter notebook walkthrough
├── gt_process.py               # Core per-experiment processing logic
├── gt_data_agg.py              # Aggregation of processed data across experiments
├── statistical_analysis.py     # Mann-Whitney U tests and output generation
├── vial_network.py             # Vial detection/tracking network utilities
├── video_processor.py          # Frame extraction and fly position tracking
├── video_converter.py          # H.264 → MP4 conversion helper
├── file_installs.txt           # Required package list
├── main_stl_files_and_folders/ # 3D-printable hardware components
├── Glaz_PolG_RNAi/             # Experiment set: Glaz × PolG RNAi crosses
└── W1118_CLKOut/               # Experiment set: W1118 × CLK-out crosses
```

## File Formats

**Input:** .h264 video files (60 fps, 1280×720) with an accompanying geotaxis_metadata.csv per subfolder.

**Per-video output:** vial-position CSVs, per-trim fly-tracking CSVs, and diagnostic plots.

**Per-experiment output:** ten aggregated CSVs (5 metrics × 2 sexes), written to Output Males / Output Females subdirectories, plus PNG trajectory/bar/heatmap plots. All CSV outputs are compatible with GraphPad Prism, R, and Excel.

**Hardware:** 3D-printable .stl files for the vial holder, tapping arm, camera mount, and base frame (main_stl_files_and_folders/).

---

## Requirements

Python 3.8+ with: PyTorch (v2.3.1+cu121), torchvision, OpenCV, NumPy, Pandas, SciPy, Statsmodels, Matplotlib, Seaborn. NVIDIA CUDA 12.1 is recommended for vial detection but the pipeline automatically falls back to CPU execution if no compatible GPU is available. Standalone executables (no Python required) are available for Windows, macOS, and Ubuntu Linux.

## Citation

If you use this repository or platform in your research, please cite:

[1] Melkani D., Harnwal N., Desai S., Patel D., Melkani G. (year) Design and Implementation of an Automated Drosophila Locomotor Assay Using Computer Vision Tracking, submitted<br>

```
@article{Melkani2026Geotaxis,
  title     = {Design and Implementation of an Automated Drosophila Locomotor Assay Using Computer Vision Tracking},
  author    = {Melkani, Dave and Harnwal, Neelaksh and Desai, Shubhankar and Patel, Dev and Melkani, Girish C.},
  journal   = {Department of Pathology, University of Alabama at Birmingham},
  year      = {2026}
}
```
