"""
A program to read multiple csv files and save as a single csv file

Sample usage:
python3 process_raw_data.py ../archive/TelevisionNews/ ../data/
"""

import argparse
import os
import pandas as pd

parser = argparse.ArgumentParser(description='Multiple csv files into a single csv file')
parser.add_argument('src', help="Path to folder with csv files")
parser.add_argument('dst', help="Path to folder where destination csv should be stored")
args = parser.parse_args()

dataframes = list()

for file in os.listdir(args.src):
    if file.endswith(".csv"):
        try:
            df = pd.read_csv(os.path.join(args.src, file), index_col=None, header=0)
            dataframes.append(df)
        except:
            print("Skipped file: ", file) #Some error in the file, maybe it is empty
    else:
        print("Invalid file: ", file)

saveframe = pd.concat(dataframes, axis=0, ignore_index=True)
saveframe.to_csv(os.path.join(args.dst, 'saved.csv'), index=False)
