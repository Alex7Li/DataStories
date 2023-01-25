import os
import pandas as pd
from pathlib import Path
import tqdm

def get_data(subset_size=0):
    data_folder = Path('data')
    filenames = os.listdir(data_folder / 'ratings')
    if subset_size != 0:
        filenames = filenames[:subset_size]
    ratings = {}
    submissions = {}
    for handlecsv in tqdm.tqdm(filenames):
        handle = handlecsv[:-4]
        ratings[handle] = pd.read_csv(data_folder / 'ratings' / handlecsv)
        submissions[handle] = pd.read_csv(data_folder / 'submissions' / handlecsv)
    return ratings, submissions

if __name__ == "__main__":
    ratings, submissions = get_data(1000)
