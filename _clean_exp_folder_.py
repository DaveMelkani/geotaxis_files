import os, shutil
from tqdm import tqdm

def clean_subfolders(parent_folder):
    for subfolder in tqdm(os.listdir(parent_folder)):
        subfolder_path = os.path.join(parent_folder, subfolder)
        if os.path.isdir(subfolder_path):
            h264_file = f"{subfolder}.h264"
            metadata_file = "genotype_metadata.csv"
            for file_name in os.listdir(subfolder_path):
                file_path = os.path.join(subfolder_path, file_name)
                if file_name not in {h264_file, metadata_file}:
                    if os.path.isfile(file_path):
                        os.remove(file_path)  # Delete file
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Delete folder

            print(f"Cleaned {subfolder_path}, keeping {h264_file} and {metadata_file}")

experiment = input("Enter experiment name (e.g., 'CS_SK2' or 'W1118_CLKOut'): ")
folder_path = f"./{experiment}"
clean_subfolders(folder_path)