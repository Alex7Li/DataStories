import os
import json
from pathlib import Path
import logging

from tqdm import tqdm
import pandas as pd
standings_data_folder = Path('cf_stats/standings_data')
metadata_path = standings_data_folder / 'standing_metadata.json'

def all_rated_contests():
    with open(metadata_path) as f:
        contest_metadata = json.load(f)
    inds = sorted(contest_metadata.keys(),
                  key=lambda x: contest_metadata[x]['end_time'])
    for contest_ind in tqdm(inds, "Going through rated contests"):
        metadata = contest_metadata[contest_ind]
        if metadata['rated']:
            file_path = standings_data_folder / \
                'standings' / f"{contest_ind}.csv"
            standings = pd.read_csv(file_path)
            yield standings
n_contests = 0
n_participants = []
for contest in all_rated_contests():
    n_contests += 1
    n_participants.append(len(contest))
print(f"There were {n_contests} contests")
