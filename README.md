# Geotaxis Files
 
A pipeline for automated video-based geotaxis assay analysis in *Drosophila*, including hardware STL files, data processing scripts, statistical analysis, and aggregated output data.
 
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
 
---
