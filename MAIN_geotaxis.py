import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import warnings
# from pandas.errors import PerformanceWarning
warnings.filterwarnings("ignore", message="Pandas requires version '1.3.6' or newer of 'bottleneck'")
warnings.filterwarnings("ignore", category=FutureWarning, module="seaborn")
warnings.filterwarnings( "ignore", category=FutureWarning, message=".*default of observed=False is deprecated and will be changed to True in a future version of pandas.*" )
# warnings.filterwarnings("ignore", category=PerformanceWarning, message=".*DataFrame is highly fragmented.*")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import zipfile, cv2,torch, torchvision, subprocess
from tqdm import tqdm
import seaborn as sns
import matplotlib.cm as cm
from PIL import Image
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from scipy.signal import find_peaks

from video_converter import VideoConverter
from video_processor import VideoProcessor
from vial_network import Vial_Network
from gt_process import Finalized_Geotaxis
from gt_data_agg import GenotypeAnalyzer
from statistical_analysis_2 import Statistical_Analysis

def main():
    experiment = input("Enter experiment name (e.g., 'CS_SK2' or 'W1118_CLKOut'): ")
    lamp_var = input("Are you using the lamp? (Yes or No): ").strip().capitalize()
    # frame_steps = int(input("Enter frame steps (e.g., 30 -> every 0.5 secs, 60 -> every 1 secs): "))
    frame_steps = 30
    stats_time_cut = float(input("Enter Stats Time Cut (e.g., 9 -> stats from 0 to 9 seconds): "))
    
    vid_clips = 4  
    temp = list(range(1, vid_clips + 1))

    spec_video_folders = [d for d in os.listdir(f"./{experiment}") 
                         if os.path.isdir(os.path.join(f"./{experiment}", d)) 
                         and d not in ('.ipynb_checkpoints', '_Output_Males', '_Output_Females')]

    for i, spec_video in tqdm(enumerate(spec_video_folders, start=1)):
        if check_required_files(experiment, spec_video):
            print(f"All required files found for {spec_video}. Skipping processing...")
            continue  # Skip to the next folder

        print(f"Processing video folder: {spec_video}")
        # ______________H264_TO_MP4_________________
        input_file = f"./{experiment}/{spec_video}/{spec_video}.h264"
        output_file = f"./{experiment}/{spec_video}/{spec_video}.mp4"

        converter = VideoConverter(input_file, output_file)
        converter.convert()
        del input_file, output_file

        # _____________VIDEO_SNIPS__________________
        video_path = f"./{experiment}/{spec_video}/{spec_video}.mp4"
        print(f"Start Video TRIMS for {spec_video}:")
        processor = VideoProcessor(video_path)
        processor.process_video()
        processor.video_filt()

        trims_ttl = vid_clips 
        for trim_cnt in range(1, trims_ttl + 1):
            start_frame = processor.frame_ranges_df.iloc[trim_cnt - 1]['start_frame']
            end_frame = processor.frame_ranges_df.iloc[trim_cnt - 1]['end_frame']
            processor.crop_video(start_frame, end_frame, trim_cnt)

        video_inputs = [f"./{experiment}/{spec_video}/TRIM_{i}_{spec_video}.mp4" for i in temp]
        output_files = [f"./{experiment}/{spec_video}/{spec_video}_output/TRIM_{i}_{spec_video}_y_positions.csv" for i in temp]
        genotype_csv_pth = f"./{experiment}/{spec_video}/genotype_metadata.csv"
        vials_to_drop, vial_num_list = geno_meta(genotype_csv_pth)

        # ______________VIAL_NETWORK___________________
        vial_pos_lists = []
        print(f"VIALS USED:\n{vial_num_list}\nVIALS USED LENGTH: {len(vial_num_list)}\n")
        for idx, vid in enumerate(video_inputs, start=1):
            print(f"Start Vial Network for {spec_video} TRIM {idx}:")
            vial_network = Vial_Network(experiment, spec_video, idx, vid, vials_to_drop, lamp_var)
            vial_network.predict_and_display()
            # vial_network.save_model("gt_newVial_nn.pth")

            vials_input = f"./{experiment}/{spec_video}/trim_{idx}_{spec_video}_vials_pos.csv"
            vial_pos_lists.append(vials_input)

        #________________GEOTAXIS_MAIN________________#
        print(f"\n\nRUNNING Video {i}/{len(spec_video_folders)}: '{os.path.basename(spec_video)}':\n")
        fin_geo = Finalized_Geotaxis(experiment=experiment, spec_vid=os.path.basename(spec_video), 
                                     fps=60, frame_step=frame_steps, top_thresh=0.75, bottom_thresh=0.80, 
                                     adder_val=150, remove_px=125)
        fin_geo.run()
        # experiment=experiment, spec_vid=os.path.basename(spec_video), fps=60, frame_step=frame_steps, top_thresh=0.50, bottom_thresh=0.55, adder_val=150, remove_px=125
    
    #________________EXPERIMENT_AGGREGATOR:________________#
    folder_path = f"./{experiment}/"
    analyzer = GenotypeAnalyzer(folder_path)
    analyzer.run()

    #________________STATISTICAL_ANALYSIS________________#
    sa = Statistical_Analysis(experiment, filter_time=stats_time_cut)
    sa.run_analysis()
    
    #________________ZIPPING_FOLDER________________
    input_folder = f'./{experiment}/'
    output_zip_path = f'./{experiment}_ZIPPED.zip'
    zipping = input("Do you want to ZIP the experiment folder? (Yes or No): ").lower()
    should_zip = zipping in ("yes", "y")
    if should_zip:
        zip_folder(input_folder, output_zip_path)

        
def geno_meta(genotype_csv_input, n=12):
    geno_df = pd.read_csv(genotype_csv_input)
    geno_df['Vial_Num'] = pd.to_numeric(geno_df['Vial_Num'], errors='coerce')
    geno_df = geno_df.dropna(subset=['Vial_Num', 'Sex']).copy()
    geno_df['Vial_Num'] = geno_df['Vial_Num'].astype(int)
    vial_num_list = geno_df["Vial_Num"].tolist()
    irrel_vials = list(set(range(1, n + 1)) - set(geno_df["Vial_Num"].tolist()))
    return irrel_vials, vial_num_list

    
def zip_folder(input_folder, output_zip_path):
    if not os.path.exists(input_folder):
        print(f"Input folder '{input_folder}' does not exist.")
        return
    
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_files = sum(len(files) for _, _, files in os.walk(input_folder))
        with tqdm(total=total_files, unit='file', desc='Zipping') as pbar:
            for root, dirs, files in os.walk(input_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, input_folder))
                    pbar.update(1)
    
    print(f"Folder '{input_folder}' has been zipped to '{output_zip_path}'.")

def check_required_files(experiment, video_folder):
    required_files_main = [
        f"{video_folder}.h264", 
        f"{video_folder}.mp4", 
        "genotype_metadata.csv",
    ]
    
    required_trim_mp4_files = [
        f"TRIM_1_{video_folder}.mp4", 
        f"TRIM_2_{video_folder}.mp4", 
        f"TRIM_3_{video_folder}.mp4", 
        f"TRIM_4_{video_folder}.mp4"
    ]

    required_trim_csv_files = [
        f"trim_1_{video_folder}_vials_pos.csv", 
        f"trim_2_{video_folder}_vials_pos.csv", 
        f"trim_3_{video_folder}_vials_pos.csv", 
        f"trim_4_{video_folder}_vials_pos.csv"
    ]

    required_csv_outputs = [
        "percentage_HP_df.csv",
        "percentage_LP_df.csv",
        "percentage_MP_df.csv",
        "position_Total_df.csv"
    ]

    required_png_outputs = [
        "percentage_HP_plot.png",
        "percentage_LP_plot.png",
        "percentage_MP_plot.png",
        "position_Total_plot.png"
    ]

    main_folder_path = f"./{experiment}/{video_folder}"
    for file in required_files_main:
        if not os.path.exists(os.path.join(main_folder_path, file)):
            print(f"Missing required main file: {file}")
            return False
    
    for file in required_trim_mp4_files:
        if not os.path.exists(os.path.join(main_folder_path, file)):
            print(f"Missing trimmed video file: {file}")
            return False
            
    for file in required_trim_csv_files:
        if not os.path.exists(os.path.join(main_folder_path, file)):
            print(f"Missing trimmed video file: {file}")
            return False

    for file in required_csv_outputs:
        if not os.path.exists(os.path.join(main_folder_path, file)):
            print(f"Missing trimmed video file: {file}")
            return False
        
    for file in required_png_outputs:
        if not os.path.exists(os.path.join(main_folder_path, file)):
            print(f"Missing trimmed video file: {file}")
            return False
    return True

if __name__ == "__main__":
    main()
