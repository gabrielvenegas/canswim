import pandas as pd
from pathlib import Path
import argparse

def check_parquets_in_folder(directory_path: str):
    """
    Checks all .parquet files in a given directory to see if they are empty.
    """
    
    # Convert the string path to a Path object
    folder = Path(directory_path)

    # Check if the directory exists
    if not folder.is_dir():
        print(f"Error: Directory not found at '{directory_path}'")
        return

    # Find all files ending with .parquet in the directory
    parquet_files = list(folder.glob('*.parquet'))

    if not parquet_files:
        print(f"No .parquet files found in '{directory_path}'")
        return

    print(f"--- Checking {len(parquet_files)} parquet files in '{directory_path}' ---\n")

    for file_path in parquet_files:
        try:
            df = pd.read_parquet(file_path)
            if df.empty:
                print(f"FILE: {file_path.name}\nSTATUS: EMPTY\n")
            else:
                print(f"FILE: {file_path.name}\nSTATUS: Contains {len(df)} rows of data.\n")
        except Exception as e:
            print(f"FILE: {file_path.name}\nSTATUS: ERROR - Could not read file.\nError: {e}\n")

if __name__ == "__main__":
    # Set up argument parser to accept a folder path from the command line
    parser = argparse.ArgumentParser(description="Check all .parquet files in a folder to see if they are empty.")
    parser.add_argument("folder_path", type=str, help="The path to the folder containing .parquet files.")
    
    args = parser.parse_args()
    
    check_parquets_in_folder(args.folder_path)
